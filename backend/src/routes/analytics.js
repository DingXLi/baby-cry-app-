/**
 * Analytics Routes - /api/v1/analytics
 */

const express = require('express');
const { query, validationResult } = require('express-validator');
const authMiddleware = require('../middleware/auth');

const router = express.Router();
router.use(authMiddleware);

// GET /api/v1/analytics/summary?period=7d|30d|all
router.get(
  '/summary',
  [query('period').optional().isIn(['1d', '7d', '30d', 'all'])],
  async (req, res, next) => {
    try {
      const { CryRecord, Sequelize } = req.app.locals.db;
      const { Op, fn, col, literal } = Sequelize;

      const period = req.query.period || '7d';
      const where = { userId: req.userId };

      if (period !== 'all') {
        const days = parseInt(period);
        where.timestamp = { [Op.gte]: new Date(Date.now() - days * 86400000) };
      }

      const [total, todayCount, typeRows] = await Promise.all([
        CryRecord.count({ where }),
        CryRecord.count({
          where: {
            ...where,
            timestamp: { [Op.gte]: new Date(new Date().setHours(0, 0, 0, 0)) },
          },
        }),
        CryRecord.findAll({
          where,
          attributes: ['cryType', [fn('COUNT', col('id')), 'count']],
          group: ['cryType'],
          raw: true,
        }),
      ]);

      const typeDistribution = {};
      for (const row of typeRows) {
        typeDistribution[row.cryType] = parseInt(row.count);
      }

      const daysSinceFirst = total > 0
        ? Math.max(1, Math.ceil((Date.now() - new Date(
            (await CryRecord.min('timestamp', { where }))
          ).getTime()) / 86400000))
        : 1;

      res.json({
        success: true,
        data: {
          period,
          totalCries: total,
          todayCries: todayCount,
          dailyAverage: parseFloat((total / daysSinceFirst).toFixed(1)),
          typeDistribution,
        },
      });
    } catch (err) {
      next(err);
    }
  }
);

// GET /api/v1/analytics/trends?period=7d&groupBy=hour|day
router.get(
  '/trends',
  [
    query('period').optional().isIn(['1d', '7d', '30d']),
    query('groupBy').optional().isIn(['hour', 'day']),
  ],
  async (req, res, next) => {
    try {
      const { CryRecord, Sequelize } = req.app.locals.db;
      const { Op, fn, col } = Sequelize;

      const period = req.query.period || '7d';
      const groupBy = req.query.groupBy || 'day';
      const days = parseInt(period);

      const where = {
        userId: req.userId,
        timestamp: { [Op.gte]: new Date(Date.now() - days * 86400000) },
      };

      const records = await CryRecord.findAll({
        where,
        attributes: ['timestamp', 'cryType'],
        order: [['timestamp', 'ASC']],
        raw: true,
      });

      // Aggregate by hour or day
      const buckets = {};
      for (const r of records) {
        const d = new Date(r.timestamp);
        const key = groupBy === 'hour'
          ? `${d.toISOString().slice(0, 13)}:00:00Z`
          : d.toISOString().slice(0, 10);

        if (!buckets[key]) buckets[key] = { total: 0 };
        buckets[key].total += 1;
        buckets[key][r.cryType] = (buckets[key][r.cryType] || 0) + 1;
      }

      const trends = Object.entries(buckets)
        .map(([time, data]) => ({ time, ...data }))
        .sort((a, b) => a.time.localeCompare(b.time));

      // Peak hours (top 3 by count)
      const hourCounts = {};
      for (const r of records) {
        const h = new Date(r.timestamp).getHours();
        hourCounts[h] = (hourCounts[h] || 0) + 1;
      }
      const peakHours = Object.entries(hourCounts)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 3)
        .map(([hour]) => parseInt(hour));

      res.json({ success: true, data: { trends, peakHours } });
    } catch (err) {
      next(err);
    }
  }
);

module.exports = router;
