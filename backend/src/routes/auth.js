/**
 * Auth Routes - /api/v1/auth
 */

const express = require('express');
const jwt = require('jsonwebtoken');
const { body, validationResult } = require('express-validator');
const authMiddleware = require('../middleware/auth');

const router = express.Router();
const JWT_SECRET = process.env.JWT_SECRET || 'dev-secret-key';
const JWT_EXPIRES_IN = process.env.JWT_EXPIRES_IN || '7d';

const signToken = (userId) =>
  jwt.sign({ userId }, JWT_SECRET, { expiresIn: JWT_EXPIRES_IN });

// POST /api/v1/auth/register
router.post(
  '/register',
  [
    body('email').isEmail().normalizeEmail(),
    body('password').isLength({ min: 6 }),
    body('name').trim().notEmpty(),
  ],
  async (req, res, next) => {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({
        success: false,
        error: { code: 'VALIDATION_ERROR', details: errors.array() },
      });
    }

    try {
      const { User } = req.app.locals.db;
      const { email, password, name } = req.body;

      const existing = await User.findOne({ where: { email } });
      if (existing) {
        return res.status(409).json({
          success: false,
          error: { code: 'EMAIL_EXISTS', message: 'Email already registered' },
        });
      }

      const user = await User.create({ email, password, name });
      const token = signToken(user.id);

      res.status(201).json({ success: true, data: { user, token } });
    } catch (err) {
      next(err);
    }
  }
);

// POST /api/v1/auth/login
router.post(
  '/login',
  [body('email').isEmail().normalizeEmail(), body('password').notEmpty()],
  async (req, res, next) => {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({
        success: false,
        error: { code: 'VALIDATION_ERROR', details: errors.array() },
      });
    }

    try {
      const { User } = req.app.locals.db;
      const { email, password } = req.body;

      const user = await User.findOne({ where: { email } });
      if (!user || !(await user.comparePassword(password))) {
        return res.status(401).json({
          success: false,
          error: { code: 'INVALID_CREDENTIALS', message: 'Invalid email or password' },
        });
      }

      const token = signToken(user.id);
      res.json({ success: true, data: { user, token } });
    } catch (err) {
      next(err);
    }
  }
);

// GET /api/v1/auth/me
router.get('/me', authMiddleware, async (req, res, next) => {
  try {
    const { User } = req.app.locals.db;
    const user = await User.findByPk(req.userId);
    if (!user) {
      return res.status(404).json({
        success: false,
        error: { code: 'NOT_FOUND', message: 'User not found' },
      });
    }
    res.json({ success: true, data: { user } });
  } catch (err) {
    next(err);
  }
});

// PATCH /api/v1/auth/settings
router.patch('/settings', authMiddleware, async (req, res, next) => {
  try {
    const { User } = req.app.locals.db;
    const user = await User.findByPk(req.userId);
    if (!user) {
      return res.status(404).json({ success: false, error: { code: 'NOT_FOUND' } });
    }

    const updatedSettings = { ...user.settings, ...req.body.settings };
    await user.update({ settings: updatedSettings });
    res.json({ success: true, data: { user } });
  } catch (err) {
    next(err);
  }
});

module.exports = router;
