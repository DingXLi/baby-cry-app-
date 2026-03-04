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
      primaryKey: true
    },
    userId: {
      type: DataTypes.UUID,
      allowNull: false,
      references: {
        model: 'users',
        key: 'id'
      }
    },
    cryType: {
      type: DataTypes.ENUM('hungry', 'sleepy', 'uncomfortable', 'normal'),
      allowNull: false
    },
    confidence: {
      type: DataTypes.FLOAT,
      allowNull: false,
      validate: {
        min: 0,
        max: 1
      }
    },
    audioUrl: {
      type: DataTypes.STRING,
      allowNull: false
    },
    duration: {
      type: DataTypes.FLOAT,
      comment: 'Duration in seconds'
    },
    notes: {
      type: DataTypes.TEXT,
      allowNull: true
    },
    timestamp: {
      type: DataTypes.DATE,
      defaultValue: DataTypes.NOW,
      comment: 'When the cry was detected'
    },
    isManual: {
      type: DataTypes.BOOLEAN,
      defaultValue: false,
      comment: 'Whether this was manually labeled'
    }
  }, {
    timestamps: true,
    tableName: 'cry_records',
    indexes: [
      {
        fields: ['userId']
      },
      {
        fields: ['timestamp']
      },
      {
        fields: ['cryType']
      }
    ]
  });

  return CryRecord;
};
