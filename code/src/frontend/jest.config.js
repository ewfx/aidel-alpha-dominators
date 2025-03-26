export default {
    //preset : 'ts-jest',
    //setupFilesAfterEnv: ['<rootDir>/setupTests.js'],
    testEnvironment: 'jsdom',
    moduleNameMapper: {
        '^@frontend/(.*)$': '<rootDir>/code/src/frontend/$1',
    },
    transform: {
      '.+\\.(css|less|scss|sass|styl)$': 'jest-css-modules-transform',
      '^.+\\.jsx?$': 'babel-jest'
    },
    collectCoverage: true,
    coverageReporters: ['json', 'lcov', 'text', 'clover'],
    coverageDirectory: '<rootDir>/coverage',
  };