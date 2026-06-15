/**
 * Baby Cry App - Backend Server
 * 🦞 虾虾开发
 */

const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const rateLimit = require('express-rate-limit');
const dotenv = require('dotenv');
const path = require('path');

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(helmet());
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Rate limiting
app.use('/api/', rateLimit({ windowMs: 60000, max: 100, standardHeaders: true }));
app.use('/api/v1/cry-records', rateLimit({ windowMs: 60000, max: 20, message: { success: false, error: { code: 'RATE_LIMIT' } } }));

// Static uploads
app.use('/uploads', express.static(path.join(__dirname, '../uploads')));

// Health check (no auth required)
app.get('/health', (req, res) => {
  res.json({
    status: 'ok',
    timestamp: new Date().toISOString(),
    service: 'baby-cry-backend',
    version: '0.2.0',
  });
});

// Database + model init
const sequelize = require('./database');
const UserModel = require('./models/User');
const CryRecordModel = require('./models/CryRecord');

const User = UserModel(sequelize);
const CryRecord = CryRecordModel(sequelize);

// Associations
User.hasMany(CryRecord, { foreignKey: 'userId', as: 'cryRecords' });
CryRecord.belongsTo(User, { foreignKey: 'userId', as: 'user' });

// Make db available to routes
app.locals.db = { User, CryRecord, Sequelize: sequelize.constructor };

// Routes
app.use('/api/v1/auth', require('./routes/auth'));
app.use('/api/v1/cry-records', require('./routes/cryRecords'));
app.use('/api/v1/analytics', require('./routes/analytics'));

// 404 handler
app.use((req, res) => {
  res.status(404).json({
    success: false,
    error: { code: 'NOT_FOUND', message: 'Route not found' },
  });
});

// Error handler
app.use((err, req, res, next) => {
  console.error('Error:', err.message);
  res.status(err.status || 500).json({
    success: false,
    error: {
      code: err.code || 'SERVER_ERROR',
      message: process.env.NODE_ENV === 'development' ? err.message : 'Internal server error',
    },
  });
});

// Start server after DB sync
sequelize.sync({ alter: false }).then(() => {
  console.log('✅ Database synced');
  app.listen(PORT, () => {
    console.log(`🦞 Baby Cry Backend running on port ${PORT}`);
    console.log(`📍 Health: http://localhost:${PORT}/health`);
  });
}).catch((err) => {
  console.error('❌ Database sync failed:', err.message);
  process.exit(1);
});

module.exports = app;
