/**
 * Cry Records Routes - /api/v1/cry-records
 */

const express = require('express');
const { body, query, validationResult } = require('express-validator');
const multer = require('multer');
const path = require('path');
const authMiddleware = require('../middleware/auth');

const router = express.Router();
router.use(authMiddleware);

const storage = multer.diskStorage({
  destination: (req, file, cb) => cb(null, path.join(__dirname, '../../uploads')),
  filename: (req, file, cb) =>
    cb(null, `${req.userId}-${Date.now()}${path.extname(file.originalname)}`),
});
const upload = multer({
  storage,
  limits: { fileSize: parseInt(process.env.MAX_FILE_SIZE) || 10 * 1024 * 1024 },
  fileFilter: (req, file, cb) => {
    const allowed = /wav|mp3|m4a|ogg/;
    cb(null, allowed.test(path.extname(file.originalname).toLowerCase()));
  },
});

const VALID_CRY_TYPES = ['hungry', 'sleepy', 'uncomfortable', 'normal'];

// GET /api/v1/cry-records
router.get(
  '/',
  [
    query('page').optional().isInt({ min: 1 }).toInt(),
    query('limit').optional().isInt({ min: 1, max: 100 }).toInt(),
    query('cryType').optional().isIn(VALID_CRY_TYPES),
    query('startDate').optional().isISO8601(),
    query('endDate').optional().isISO8601(),
  ],
  async (req, res, next) => {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ success: false, error: { code: 'VALIDATION_ERROR', details: errors.array() } });
    }

    try {
      const { CryRecord, Sequelize } = req.app.locals.db;
      const { Op } = Sequelize;
      const page = req.query.page || 1;
      const limit = req.query.limit || 20;
      const offset = (page - 1) * limit;

      const where = { userId: req.userId };
      if (req.query.cryType) where.cryType = req.query.cryType;
      if (req.query.startDate || req.query.endDate) {
        where.timestamp = {};
        if (req.query.startDate) where.timestamp[Op.gte] = new Date(req.query.startDate);
        if (req.query.endDate) where.timestamp[Op.lte] = new Date(req.query.endDate);
      }

      const { count, rows } = await CryRecord.findAndCountAll({
        where,
        order: [['timestamp', 'DESC']],
        limit,
        offset,
      });

      res.json({
        success: true,
        data: {
          records: rows,
          pagination: {
            total: count,
            page,
            limit,
            totalPages: Math.ceil(count / limit),
          },
        },
      });
    } catch (err) {
      next(err);
    }
  }
);

// POST /api/v1/cry-records
router.post(
  '/',
  upload.single('audio'),
  [
    body('cryType').isIn(VALID_CRY_TYPES),
    body('confidence').isFloat({ min: 0, max: 1 }),
    body('duration').optional().isFloat({ min: 0 }),
    body('notes').optional().trim(),
    body('timestamp').optional().isISO8601(),
    body('isManual').optional().isBoolean(),
  ],
  async (req, res, next) => {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ success: false, error: { code: 'VALIDATION_ERROR', details: errors.array() } });
    }

    try {
      const { CryRecord } = req.app.locals.db;
      const audioUrl = req.file
        ? `/uploads/${req.file.filename}`
        : req.body.audioUrl || 'local://recording';

      const record = await CryRecord.create({
        userId: req.userId,
        cryType: req.body.cryType,
        confidence: parseFloat(req.body.confidence),
        audioUrl,
        duration: req.body.duration ? parseFloat(req.body.duration) : null,
        notes: req.body.notes || null,
        timestamp: req.body.timestamp ? new Date(req.body.timestamp) : new Date(),
        isManual: req.body.isManual === 'true' || req.body.isManual === true,
      });

      res.status(201).json({ success: true, data: { record } });
    } catch (err) {
      next(err);
    }
  }
);

// GET /api/v1/cry-records/:id
router.get('/:id', async (req, res, next) => {
  try {
    const { CryRecord } = req.app.locals.db;
    const record = await CryRecord.findOne({
      where: { id: req.params.id, userId: req.userId },
    });

    if (!record) {
      return res.status(404).json({ success: false, error: { code: 'NOT_FOUND' } });
    }
    res.json({ success: true, data: { record } });
  } catch (err) {
    next(err);
  }
});

// PATCH /api/v1/cry-records/:id
router.patch(
  '/:id',
  [
    body('notes').optional().trim(),
    body('isManual').optional().isBoolean(),
    body('cryType').optional().isIn(VALID_CRY_TYPES),
  ],
  async (req, res, next) => {
    try {
      const { CryRecord } = req.app.locals.db;
      const record = await CryRecord.findOne({
        where: { id: req.params.id, userId: req.userId },
      });

      if (!record) {
        return res.status(404).json({ success: false, error: { code: 'NOT_FOUND' } });
      }

      const updates = {};
      if (req.body.notes !== undefined) updates.notes = req.body.notes;
      if (req.body.isManual !== undefined) updates.isManual = req.body.isManual;
      if (req.body.cryType !== undefined) updates.cryType = req.body.cryType;

      await record.update(updates);
      res.json({ success: true, data: { record } });
    } catch (err) {
      next(err);
    }
  }
);

// DELETE /api/v1/cry-records/:id
router.delete('/:id', async (req, res, next) => {
  try {
    const { CryRecord } = req.app.locals.db;
    const record = await CryRecord.findOne({
      where: { id: req.params.id, userId: req.userId },
    });

    if (!record) {
      return res.status(404).json({ success: false, error: { code: 'NOT_FOUND' } });
    }

    await record.destroy();
    res.json({ success: true, data: { message: 'Record deleted' } });
  } catch (err) {
    next(err);
  }
});

module.exports = router;
