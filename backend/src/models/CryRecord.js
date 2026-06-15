/**
 * CryRecord Model
 * 🦞 虾虾开发
 */

const { DataTypes } = require('sequelize');

module.exports = (sequelize) => {
  const CryRecord = sequelize.define('CryRecord', {
    id: {
      type: DataTypes.UUID,
      defaultValue: DataTypes.UUIDV4,
      primaryKey: true,
    },
    userId: {
      type: DataTypes.UUID,
      allowNull: false,
    },
    cryType: {
      type: DataTypes.STRING(20),
      allowNull: false,
      validate: {
        isIn: [['hungry', 'sleepy', 'uncomfortable', 'normal']],
      },
    },
    confidence: {
      type: DataTypes.FLOAT,
      allowNull: false,
      validate: { min: 0, max: 1 },
    },
    audioUrl: {
      type: DataTypes.STRING,
      allowNull: false,
      defaultValue: 'local://recording',
    },
    duration: {
      type: DataTypes.FLOAT,
      allowNull: true,
    },
    notes: {
      type: DataTypes.TEXT,
      allowNull: true,
    },
    timestamp: {
      type: DataTypes.DATE,
      defaultValue: DataTypes.NOW,
    },
    isManual: {
      type: DataTypes.BOOLEAN,
      defaultValue: false,
    },
  }, {
    timestamps: true,
    tableName: 'cry_records',
    indexes: [
      { fields: ['userId'] },
      { fields: ['timestamp'] },
      { fields: ['cryType'] },
    ],
  });

  return CryRecord;
};
