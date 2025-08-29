# Database Implementation Plan for Shrinkage Coefficient Calculation System

## 1. Overview

This document presents a detailed implementation plan for a comprehensive database system for the shrinkage coefficient calculation system. The system is designed for the fish processing industry to accurately calculate and analyze nonlinear shrinkage coefficients during production using adaptive machine learning models.

The database is implemented using PostgreSQL with TimescaleDB extension for time-series optimization, SQLAlchemy ORM for Python integration, and supports PL/Python for executing Python scripts within the database. The system includes eighteen tables with seamless integration into existing ShrinkageSystem and AdaptiveShrinkageModel components.

## 1.1 Implementation Status

Most of the database functionality has already been implemented in the project. This document describes both the already implemented components and areas for improvement and additional functionality that need to be added for full system implementation.

## 2. Architecture

### 2.1 System Components

The database implementation will consist of the following components:

1. **Database Schema Layer**: Defines table structure, relationships and constraints
2. **ORM Layer**: SQLAlchemy models that map to database tables
3. **Service Layer**: Business logic for database operations
4. **Integration Layer**: Interfaces between the database and existing system components
5. **Migration System**: Alembic-based system for schema versioning and updates
6. **CLI Tools**: Command-line utilities for database management

### 2.2 Technology Stack

- **Database**: PostgreSQL with TimescaleDB extension
- **ORM**: SQLAlchemy
- **Migration Tool**: Alembic
- **Connection Pool**: Built-in SQLAlchemy pool
- **Database Monitoring**: Custom analytics and logging

### 2.3 Component Interaction Diagram

```
graph TD
    A[ShrinkageSystem] --> B[DatabaseIntegration]
    C[AdaptiveShrinkageModel] --> B
    D[DataProcessor] --> B
    E[ReportingSystem] --> B
    F[GUI Components] --> B
    
    B --> G[DatabaseService]
    G --> H[SQLAlchemy ORM]
    H --> I[(PostgreSQL + TimescaleDB)]
    
    J[MigrationSystem] --> I
    K[CLI Tools] --> I
```

## 3. Database Schema Design

### 3.1 Entity Relationship Diagram

```
erDiagram
    NOMENCLATURE ||--o{ CALCULATION_DATA : has
    NOMENCLATURE ||--o{ SURPLUS_SPECIFICATIONS : has
    NOMENCLATURE ||--o{ SURPLUS_RECOMMENDATIONS : has
    NOMENCLATURE ||--o{ SURPLUS_PATTERNS : has
    NOMENCLATURE ||--o{ ANALYTICS : contains
    
    SOURCE_DATA ||--o{ CALCULATION_DATA : contains
    
    CALCULATION_DATA ||--o{ COEFFICIENTS : produces
    CALCULATION_DATA ||--o{ VALIDATION_ERRORS : generates
    CALCULATION_DATA ||--o{ PRELIMINARY_FORECASTS : generates
    CALCULATION_DATA ||--o{ DATA_LINEAGE : tracks
    
    MODELS ||--o{ COEFFICIENTS : defines
    MODELS ||--o{ FORECASTS : generates
    MODELS ||--o{ PRELIMINARY_FORECASTS : generates
    MODELS ||--o{ ML_MODEL_REGISTRY : registers
    
    COEFFICIENTS ||--o{ FORECASTS : predicts
    
    SURPLUS_PATTERNS ||--o{ PATTERN_VALIDATIONS : validates
    
    ML_MODEL_REGISTRY ||--o{ ANALYTICS : provides
    
    PRIORITY_PERIODS }|--o{ ANALYTICS : influences
    
    AIPATTERNS }|--o{ ANALYTICS : contributes
    
    FEEDBACK_PREFERENCES ||--o{ SURPLUS_PATTERNS : configures
```

### 3.2 Table Definitions

#### 3.2.1 SourceData Table
Stores information about source data files.

| Column | Type | Description |
|--------|------|-------------|
| id | Integer (PK) | Primary key |
| file_name | String | Source file name |
| file_path | String | Source file path |
| upload_date | DateTime | File upload date |
| file_hash | String | Hash for file integrity verification |
| processed | Boolean | Whether the file has been processed |
| quality_score | Float | Data quality score |

#### 3.2.2 Nomenclature Table
Stores information about product nomenclature.

| Column | Type | Description |
|--------|------|-------------|
| id | Integer (PK) | Primary key |
| name | String | Product name |
| product_type | String | Product type |
| product_type_code | String | Product type code |
| created_date | DateTime | Record creation date |
| validation_flags | String | Validation flags |

#### 3.2.3 CalculationData Table
Stores normalized data for calculations.

| Column | Type | Description |
|--------|------|-------------|
| id | Integer (PK) | Primary key |
| source_data_id | Integer (FK) | Reference to source data |
| nomenclature_id | Integer (FK) | Reference to nomenclature |
| initial_balance | Float | Initial inventory balance |
| incoming | Float | Incoming quantity |
| outgoing | Float | Outgoing quantity |
| final_balance | Float | Final inventory balance |
| storage_days | Integer | Storage period in days |
| calculation_date | DateTime | Calculation date |
| data_quality_flag | String | Data quality flag |
| inventory_confidence | Float | Inventory data confidence level |
| inventory_period_start | DateTime | Inventory period start |
| inventory_period_end | DateTime | Inventory period end |
| is_valid_inventory_period | Boolean | Validity of inventory period |
| is_preliminary_forecast | Boolean | Whether this is a preliminary forecast |
| preliminary_period_end | DateTime | Preliminary period end |
| human_error_probability | Float | Human error probability |
| validation_errors | Text | Validation errors |
| manual_review_required | Boolean | Whether manual review is required |
| pre_shrinkage_days | Integer | Pre-shrinkage days |
| pre_shrinkage_amount | Float | Pre-shrinkage amount |
| adjusted_shrinkage_rate | Float | Adjusted shrinkage rate |
| inventory_shrinkage_total | Float | Total inventory shrinkage |
| actual_deduction_batch | String | Actual deduction batch |
| fifo_principle_applied | Boolean | Whether FIFO principle was applied |
| fifo_batch_sequence | JSON | FIFO batch sequence |

#### 3.2.4 Models Table
Stores information about calculation models.

| Column | Type | Description |
|--------|------|-------------|
| id | Integer (PK) | Primary key |
| name | String | Model name |
| model_type | String | Model type |
| description | Text | Model description |
| version | String | Model version |
| created_date | DateTime | Creation date |

#### 3.2.5 Coefficients Table
Stores calculated coefficients.

| Column | Type | Description |
|--------|------|-------------|
| id | Integer (PK) | Primary key |
| calculation_data_id | Integer (FK) | Reference to calculation data |
| model_id | Integer (FK) | Reference to model |
| coefficient_a | Float | Coefficient A |
| coefficient_b | Float | Coefficient B |
| coefficient_c | Float | Coefficient C |
| accuracy_r2 | Float | R-squared accuracy |
| calculation_date | DateTime | Calculation date |
| adjusted_for_pre_shrinkage | Boolean | Whether adjusted for pre-shrinkage |
| pre_shrinkage_factor | Float | Pre-shrinkage factor |
| effective_shrinkage_rate | Float | Effective shrinkage rate |

#### 3.2.6 Forecast Table
Stores shrinkage forecasts.

| Column | Type | Description |
|--------|------|-------------|
| id | Integer (PK) | Primary key |
| coefficient_id | Integer (FK) | Reference to coefficient |
| forecast_value | Float | Forecasted value |
| actual_value | Float | Actual value |
| deviation | Float | Deviation from actual |
| forecast_date | DateTime | Forecast date |

#### 3.2.7 Analytics Table
Stores aggregated analytical data.

| Column | Type | Description |
|--------|------|-------------|
| id | Integer (PK) | Primary key |
| nomenclature_id | Integer (FK) | Reference to nomenclature |
| model_id | Integer (FK) | Reference to model |
| avg_accuracy | Float | Average accuracy |
| total_calculations | Integer | Total calculations |
| period_start | DateTime | Analysis period start |
| period_end | DateTime | Analysis period end |
| last_updated | DateTime | Last update timestamp |

#### 3.2.8 AIPatterns Table
Stores patterns and anomalies detected by AI.

| Column | Type | Description |
|--------|------|-------------|
| id | Integer (PK) | Primary key |
| pattern_type | String | Pattern type |
| description | Text | Pattern description |
| confidence_level | Float | Confidence level |
| affected_nomenclature | String | Affected nomenclature |
| discovery_date | DateTime | Discovery date |
| pattern_data | JSON | Pattern data |

#### 3.2.9 ValidationErrors Table
Stores errors found in data.

| Column | Type | Description |
|--------|------|-------------|
| id | Integer (PK) | Primary key |
| calculation_data_id | Integer (FK) | Reference to calculation data |
| error_type | String | Error type |
| description | Text | Error description |
| severity_level | String | Severity level |
| detected_by | String | Detector component |
| detection_date | DateTime | Detection date |
| resolved | Boolean | Whether resolved |
| resolution_date | DateTime | Resolution date |
| notes | Text | Additional notes |

#### 3.2.10 PriorityPeriods Table
Stores information about priority analysis periods.

| Column | Type | Description |
|--------|------|-------------|
| id | Integer (PK) | Primary key |
| period_start | DateTime | Period start |
| period_end | DateTime | Period end |
| priority_level | Integer | Priority level |
| description | Text | Description |
| created_by | String | Creator |
| created_date | DateTime | Creation date |
| active | Boolean | Whether active |

#### 3.2.11 PreliminaryForecasts Table
Stores preliminary shrinkage forecasts.

| Column | Type | Description |
|--------|------|-------------|
| id | Integer (PK) | Primary key |
| calculation_data_id | Integer (FK) | Reference to calculation data |
| forecast_model_id | Integer (FK) | Reference to forecast model |
| forecast_period_days | Integer | Forecast period in days |
| expected_shrinkage | Float | Expected shrinkage |
| confidence_level | Float | Confidence level |
| forecast_date | DateTime | Forecast date |
| actual_shrinkage | Float | Actual shrinkage |
| forecast_accuracy | Float | Forecast accuracy |
| notes | Text | Additional notes |
| pre_shrinkage_adjusted | Boolean | Whether adjusted for pre-shrinkage |
| adjusted_expected_shrinkage | Float | Adjusted expected shrinkage |
| batch_storage_history | JSON | Batch storage history |

#### 3.2.12 SurplusSpecifications Table
Stores periodic surplus specifications for products.

| Column | Type | Description |
|--------|------|-------------|
| id | Integer (PK) | Primary key |
| nomenclature_id | Integer (FK) | Reference to nomenclature |
| surplus_percentage | Float | Surplus percentage |
| specification_start_date | DateTime | Specification start date |
| specification_end_date | DateTime | Specification end date |
| is_active | Boolean | Whether active |
| created_date | DateTime | Creation date |
| created_by | String | Creator |
| notes | Text | Additional notes |

#### 3.2.13 SurplusRecommendations Table
Stores automatically generated surplus recommendations.

| Column | Type | Description |
|--------|------|-------------|
| id | Integer (PK) | Primary key |
| nomenclature_id | Integer (FK) | Reference to nomenclature |
| recommended_surplus_percentage | Float | Recommended surplus percentage |
| confidence_level | Float | Confidence level |
| analysis_period_start | DateTime | Analysis period start |
| analysis_period_end | DateTime | Analysis period end |
| calculation_method | String | Calculation method |
| supporting_data | JSON | Supporting data |
| created_date | DateTime | Creation date |
| is_accepted | Boolean | Whether accepted |
| acceptance_date | DateTime | Acceptance date |

#### 3.2.14 SurplusPatterns Table
Stores information about permanent surplus patterns.

| Column | Type | Description |
|--------|------|-------------|
| id | Integer (PK) | Primary key |
| nomenclature_id | Integer (FK) | Reference to nomenclature |
| product_type | String | Product type |
| surplus_percentage | Float | Surplus percentage |
| pattern_condition | String | Pattern condition |
| is_active | Boolean | Whether active |
| created_date | DateTime | Creation date |
| created_from_recommendation_id | Integer (FK) | Reference to recommendation |
| validation_count | Integer | Validation count |
| last_validated_date | DateTime | Last validation date |
| confidence_level | Float | Confidence level |
| feedback_count | Integer | Feedback count |
| last_feedback_date | DateTime | Last feedback date |

#### 3.2.15 PatternValidations Table
Stores validation results and feedback for automatic patterns.

| Column | Type | Description |
|--------|------|-------------|
| id | Integer (PK) | Primary key |
| surplus_pattern_id | Integer (FK) | Reference to surplus pattern |
| validation_date | DateTime | Validation date |
| actual_surplus_percentage | Float | Actual surplus percentage |
| predicted_surplus_percentage | Float | Predicted surplus percentage |
| deviation | Float | Deviation |
| validation_result | String | Validation result |
| user_feedback | Text | User feedback |
| is_confirmed | Boolean | Whether confirmed |
| confirmation_date | DateTime | Confirmation date |

#### 3.2.16 FeedbackPreferences Table
Stores flexible feedback settings.

| Column | Type | Description |
|--------|------|-------------|
| id | Integer (PK) | Primary key |
| feedback_frequency | String | Feedback frequency |
| auto_confirm_threshold | Float | Auto-confirm threshold |
| is_active | Boolean | Whether active |
| created_date | DateTime | Creation date |
| updated_date | DateTime | Update date |

#### 3.2.17 DataLineage Table
Stores data lineage information for audit purposes.

| Column | Type | Description |
|--------|------|-------------|
| id | Integer (PK) | Primary key |
| source_file_id | Integer (FK) | Reference to source file |
| calculation_data_id | Integer (FK) | Reference to calculation data |
| process_name | String | Process name |
| process_timestamp | DateTime | Process timestamp |
| user_id | String | User ID |
| input_records | Integer | Number of input records |
| output_records | Integer | Number of output records |
| status | String | Process status |
| error_message | Text | Error message |
| execution_time_ms | Integer | Execution time in milliseconds |
| version | String | Version |

#### 3.2.18 MLModelRegistry Table
Stores information about shrinkage calculation model versions.

| Column | Type | Description |
|--------|------|-------------|
| id | Integer (PK) | Primary key |
| model_name | String | Model name |
| version | String | Model version |
| algorithm_type | String | Algorithm type |
| parameters | JSON | Model parameters |
| training_date | DateTime | Training date |
| accuracy_metrics | JSON | Accuracy metrics |
| is_active | Boolean | Whether active |
| created_by | String | Creator |
| created_date | DateTime | Creation date |
| notes | Text | Additional notes |

## 4. ORM Model Implementation

### 4.1 Base Model Structure
All models inherit from the Base class which provides common functionality. The current implementation does not include automatic created_at and updated_at fields in the base class, but all models contain the necessary fields for identification and timestamps.

The current model implementation is in the file `src/core/database/models.py` and includes all eighteen tables described in section 3.2.

### 4.2 Model Relationships
ORM models implement proper relationships using SQLAlchemy relationship functions. In the current implementation, all necessary relationships between entities have already been defined:

```
# Example of relationship implementation from existing code
class Nomenclature(Base):
    __tablename__ = 'nomenclature'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    product_type = Column(String)
    created_date = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    calculation_data = relationship("CalculationData", back_populates="nomenclature")
    surplus_specifications = relationship("SurplusSpecification", back_populates="nomenclature")
    # ... other relationships

class CalculationData(Base):
    __tablename__ = 'calculation_data'
    
    id = Column(Integer, primary_key=True)
    nomenclature_id = Column(Integer, ForeignKey('nomenclature.id'))
    initial_balance = Column(Float)
    incoming = Column(Float)
    outgoing = Column(Float)
    final_balance = Column(Float)
    storage_days = Column(Integer)
    calculation_date = Column(DateTime, default=datetime.utcnow)
    # ... other fields
    
    # Relationships
    nomenclature = relationship("Nomenclature", back_populates="calculation_data")
    coefficients = relationship("Coefficient", back_populates="calculation_data")
    # ... other relationships
```

### 4.3 Areas for Improvement

1. Add a BaseModel class with automatic created_at and updated_at fields
2. Improve model documentation
3. Add additional indexes for query optimization
4. Implement caching for frequently requested data

## 5. Service Layer Implementation

### 5.1 DatabaseService Class
The DatabaseService class provides CRUD operations for most entities. The current implementation is in the file `src/core/database/services.py` and includes methods for working with the main entities:

```
# Example from existing implementation
class DatabaseService:
    def __init__(self, session: Session):
        self.session = session
    
    def create_nomenclature(self, name: str, product_type: str = None, **kwargs) -> Nomenclature:
        # Implementation of nomenclature creation with duplicate checking
        pass
    
    def get_nomenclature_by_name(self, name: str) -> Optional[Nomenclature]:
        # Implementation of nomenclature search by name
        pass
    
    def create_calculation_data(self, source_data_id: int, nomenclature_id: int, **kwargs) -> CalculationData:
        # Implementation of calculation data creation
        pass
    
    def get_calculation_data_by_nomenclature(self, nomenclature_id: int) -> List[CalculationData]:
        # Implementation of getting calculation data by nomenclature
        pass
    
    def create_model(self, name: str, model_type: str, version: str = "1.0", **kwargs) -> Model:
        # Implementation of model creation
        pass
    
    # ... other methods for other entities
```

### 5.2 Specialized Services
Some specialized services are already partially implemented but require further development:

1. **AnalyticsService**: Partially implemented through the Analytics table, but requires functionality expansion
2. **AIService**: Used through the AIPatterns table, but needs expansion
3. **PriorityPeriodService**: Implemented through the PriorityPeriods table
4. **SurplusService**: Partially implemented through the SurplusSpecification, SurplusRecommendation, SurplusPattern tables
5. **DataLineageService**: Implemented through the DataLineage table
6. **MLModelRegistryService**: Implemented through the MLModelRegistry table

### 5.3 Areas for Improvement

1. Implement missing CRUD methods for all entities
2. Add search and filtering methods for all tables
3. Implement pagination for large datasets
4. Add transaction safety
5. Implement query result caching

## 6. Integration with Existing System

### 6.1 ShrinkageSystem Integration
The existing ShrinkageSystem is already partially integrated with the database through the DatabaseIntegration class:

1. Saving calculation results to the database (implemented)
2. Loading historical data for adaptive models (partially implemented)
3. Tracking data lineage through the processing pipeline (implemented through DataLineage)

The current implementation is in the file `src/core/database/integration.py`.

### 6.2 Calculator Integration
ShrinkageCalculator and AdaptiveShrinkageModel are partially adapted for:

1. Saving models to the database (implemented through the Models table)
2. Getting historical coefficients for adaptation (partially implemented)
3. Logging calculation parameters and results (implemented through the Coefficient and CalculationData tables)

### 6.3 DataProcessor Integration
DataProcessor is partially adapted for:

1. Saving intermediate processing results (implemented through CalculationData)
2. Tracking data quality metrics (implemented through data quality fields)
3. Logging processing steps for audit purposes (implemented through DataLineage)

### 6.4 Reporting Integration
Reporting components are partially adapted for:

1. Getting data from the database (implemented)
2. Saving generated reports (requires implementation)
3. Providing access to historical reports (requires implementation)

### 6.5 GUI Integration
GUI components are partially adapted for:

1. Displaying information stored in the database (requires implementation)
2. User interaction with database entities (requires implementation)
3. Real-time data visualization (requires implementation)

### 6.6 Areas for Improvement

1. Expand ShrinkageSystem integration for full database feature support
2. Add TimescaleDB support for time-series optimization
3. Implement caching for frequently requested data
4. Add batch operations support for performance improvement
5. Expand GUI component integration

## 7. Migration System

### 7.1 Alembic Configuration
The migration system uses Alembic with the following structure:

```
src/core/database/alembic/
├── env.py
├── README
├── script.py.mako
└── versions/
    ├── 001_initial_schema.py
    ├── 002_add_priority_periods.py
    ├── 003_add_preliminary_forecasts.py
    └── ...
```

The current configuration is in the file `src/core/database/alembic.ini`.

### 7.2 Migration Process
1. Creating initial migration for the current schema (implemented)
2. Implementing the migration application process (implemented)
3. Ensuring data safety during updates (requires improvement)
4. Creating rollback mechanisms (requires implementation)
5. Testing the migration process with sample data (requires implementation)

### 7.3 Areas for Improvement

1. Add automatic migration creation when models change
2. Implement migration rollback mechanisms
3. Add data integrity checks before migration
4. Implement backup mechanisms before migration
5. Add tests for migrations

## 8. Performance Optimization

### 8.1 Indexing Strategy
- Primary keys are automatically indexed
- Foreign keys are indexed for join performance
- Time-series data is indexed with TimescaleDB
- Composite indexes for common query patterns
- Full-text search indexes for text fields

The current implementation includes basic indexes but requires additional optimization.

### 8.2 Query Optimization
- Using SQLAlchemy query optimization techniques
- Implementing connection pooling (partially implemented)
- Caching frequently requested data (requires implementation)
- Batch operations for bulk inserts/updates (requires implementation)

### 8.3 TimescaleDB Integration
- Time-series optimization for calculation data (requires implementation)
- Automatic partitioning of time-series data (requires implementation)
- Using TimescaleDB-specific functions (requires implementation)
- Continuous aggregates for analytics (requires implementation)

### 8.4 Areas for Improvement

1. Add composite indexes for frequently used queries
2. Implement query result caching
3. Optimize table joins
4. Add TimescaleDB support for time series
5. Implement pagination for large datasets
6. Add query performance monitoring

## 9. Testing Strategy

### 9.1 Unit Testing
- Testing each ORM model for proper mapping (implemented)
- Testing CRUD operations for all entities (partially implemented)
- Testing relationship integrity (requires implementation)
- Testing validation logic (requires implementation)

### 9.2 Integration Testing
- Testing database integration with ShrinkageSystem (partially implemented)
- Testing data flow between components (requires implementation)
- Testing performance with large datasets (requires implementation)
- Testing the migration process (requires implementation)

### 9.3 Real Data Testing
- Testing with actual inventory data (requires implementation)
- Validating calculation accuracy (requires implementation)
- Testing system stability (requires implementation)
- Performance benchmarking (requires implementation)

### 9.4 Areas for Improvement

1. Create a comprehensive set of unit tests for all models
2. Implement integration tests for all components
3. Add performance tests
4. Create tests with real data from the 'source_data' directory
5. Add tests for migrations
6. Implement automatic testing with each schema change

## 10. Implementation Roadmap

### Phase 1: Database Structure (COMPLETED)
1. Define complete database schema (COMPLETED)
2. Create ER diagram for visualization (COMPLETED)
3. Implement SQLAlchemy models (COMPLETED)
4. Create database initialization scripts (COMPLETED)
5. Implement basic indexing strategy (PARTIALLY COMPLETED)

### Phase 2: Service Layer (IN PROGRESS)
1. Implement DatabaseService with CRUD operations (PARTIALLY COMPLETED)
2. Create specialized services (Analytics, AI, etc.) (IN PROGRESS)
3. Implement data access patterns (IN PROGRESS)
4. Add validation and error handling (REQUIRED)
5. Create unit tests for services (REQUIRED)

### Phase 3: System Integration (IN PROGRESS)
1. Integration with ShrinkageSystem (PARTIALLY COMPLETED)
2. Adapt calculators to use the database (PARTIALLY COMPLETED)
3. Modify data processor for database operations (PARTIALLY COMPLETED)
4. Update reporting to use the database (REQUIRED)
5. Adapt GUI components for database access (REQUIRED)

### Phase 4: Testing and Optimization (NOT STARTED)
1. Conduct unit testing (NOT STARTED)
2. Perform integration testing (NOT STARTED)
3. Optimize database queries (NOT STARTED)
4. Test with real inventory data (NOT STARTED)
5. Performance tuning (NOT STARTED)

### 10.1 Updated Roadmap for PostgreSQL Implementation

#### Week 1: PostgreSQL Configuration and Migration
1. Update database configuration to use PostgreSQL instead of SQLite
2. Configure connection pooling for PostgreSQL
3. Set up TimescaleDB extension
4. Create database migration scripts for PostgreSQL

#### Week 2: Performance Optimization
1. Implement TimescaleDB for time-series data optimization
2. Add composite indexes for frequently used queries
3. Optimize existing queries for PostgreSQL
4. Implement connection pooling configuration

#### Week 3: Advanced Features
1. Implement continuous aggregates for analytics
2. Add partitioning for large time-series tables
3. Implement materialized views for complex queries
4. Add query performance monitoring

#### Week 4: Testing and Validation
1. Test migration from SQLite to PostgreSQL
2. Validate data integrity after migration
3. Performance testing with PostgreSQL
4. Update documentation for PostgreSQL deployment

## 11. Deployment Considerations

### 11.1 Database Setup
- Installing PostgreSQL with TimescaleDB extension (REQUIRED)
- Configuration for optimal performance (PARTIALLY IMPLEMENTED)
- Security setup (users, access rights) (REQUIRED)
- Backup and recovery procedures (PARTIALLY IMPLEMENTED)

The current implementation uses SQLite for simplified deployment, but for production environments, migration to PostgreSQL with TimescaleDB is required.

### 11.2 Migration Process
- Zero-downtime migration strategy (REQUIRED)
- Data backup before migration (PARTIALLY IMPLEMENTED)
- Rollback procedures (REQUIRED)
- Migrated data validation (REQUIRED)

### 11.3 Monitoring and Maintenance
- Database performance monitoring (REQUIRED)
- Regular maintenance tasks (PARTIALLY IMPLEMENTED)
- Log analysis for problem detection (REQUIRED)
- Capacity planning (REQUIRED)

### 11.4 Areas for Improvement

1. Implement PostgreSQL with TimescaleDB support
2. Add automatic backup
3. Implement performance monitoring
4. Add tools for query analysis and optimization
5. Create automatic deployment scripts
6. Implement scaling mechanisms

## 12. Risk Mitigation

### 12.1 Data Loss Prevention
- Regular automatic backups (PARTIALLY IMPLEMENTED)
- Transaction safety with rollback capability (IMPLEMENTED)
- Data validation before saving (PARTIALLY IMPLEMENTED)
- Audit of all operations (PARTIALLY IMPLEMENTED)

### 12.2 Performance Issues
- Query and indexing optimization (PARTIALLY IMPLEMENTED)
- Connection pooling (PARTIALLY IMPLEMENTED)
- Caching strategies (REQUIRED)
- Monitoring and alerts (REQUIRED)

### 12.3 Integration Issues
- Comprehensive testing strategy (REQUIRED)
- Gradual deployment approach (IMPLEMENTED)
- Rollback mechanisms (REQUIRED)
- Detailed documentation (PARTIALLY IMPLEMENTED)

### 12.4 Additional Measures

1. Implement transaction safety for all operations
2. Add failure recovery mechanisms
3. Create error notification system
4. Implement logging of all operations with detail levels
5. Add data integrity control mechanisms
6. Create disaster recovery plan

## 13. Additional Functionality to Implement

### 13.1 Advanced Analytics
1. Implement data aggregation functions across various dimensions
2. Add support for window functions for trend analysis
3. Create views for frequently requested analytical data
4. Implement support for custom analytical queries

### 13.2 Machine Learning and AI
1. Integrate Scikit-learn for shrinkage pattern analysis
2. Implement anomaly detection algorithms in data
3. Add support for clustering to group similar products
4. Create mechanisms for automatic model improvement based on feedback

### 13.3 Data Versioning
1. Implement version control system for models and coefficients
2. Add support for rollback to previous versions
3. Create model version comparison mechanism
4. Implement audit of data changes

### 13.4 Enhanced Reporting Capabilities
1. Create report generator with custom templates
2. Add data export to various formats (Excel, CSV, PDF)
3. Implement automatic report scheduler
4. Add support for interactive dashboards

### 13.5 Improved Data Management
1. Implement data import/export functions
2. Add support for bulk operations (update, delete)
3. Create mechanism for cleaning up obsolete data
4. Implement archiving of historical data

# План реализации PostgreSQL для агента Qoder

## 1. Обзор

Этот документ описывает план реализации полноценной поддержки PostgreSQL в системе расчета коэффициентов усушки с использованием агента Qoder. С учетом того, что PostgreSQL уже установлена, план фокусируется на интеграции, оптимизации и расширении функциональности системы базы данных.

## 2. Текущее состояние

### 2.1 Анализ существующей конфигурации
На основе анализа файлов проекта:
- В файле `requirements.txt` уже указаны необходимые зависимости: `sqlalchemy>=2.0.0`, `alembic>=1.10.0`, `psycopg2-binary>=2.9.0`
- В файле `src/core/database/database.py` реализована система подключения к базе данных, но по умолчанию используется SQLite
- ORM модели для всех 18 таблиц уже реализованы в `src/core/database/models.py`
- Сервисный слой частично реализован в `src/core/database/services.py`
- Интеграция с системой частично реализована в `src/core/database/integration.py`

### 2.2 Области для улучшения
1. Переключение с SQLite на PostgreSQL
2. Настройка пула соединений для PostgreSQL
3. Интеграция TimescaleDB для оптимизации временных рядов
4. Оптимизация индексов для PostgreSQL
5. Реализация миграций для PostgreSQL

## 3. План реализации для агента Qoder

### 3.1 Этап 1: Конфигурация PostgreSQL (День 1-2)

#### Задачи для агента Qoder:
1. Обновить `src/core/database/database.py` для использования PostgreSQL:
   - Изменить функцию `get_database_url()` для возврата PostgreSQL URL
   - Настроить параметры подключения для PostgreSQL
   - Реализовать правильную обработку ошибок подключения

2. Создать конфигурационный файл для параметров подключения:
   - Файл `src/core/database/config.py`
   - Поддержка переменных окружения для параметров подключения
   - Защита учетных данных

3. Проверить и при необходимости обновить зависимости:
   - Убедиться, что `psycopg2-binary` установлен
   - Проверить совместимость версий SQLAlchemy

#### Ожидаемый результат:
- Система успешно подключается к PostgreSQL
- Все параметры подключения настраиваются через конфигурацию
- Реализована обработка ошибок подключения

### 3.2 Этап 2: Миграция схемы данных (День 3-4)

#### Задачи для агента Qoder:
1. Создать миграции Alembic для PostgreSQL:
   - Инициализировать Alembic для PostgreSQL
   - Создать миграции для всех 18 таблиц
   - Убедиться в правильности типов данных для PostgreSQL

2. Адаптировать модели для PostgreSQL:
   - Проверить совместимость типов данных
   - Оптимизировать индексы для PostgreSQL
   - Добавить специфичные для PostgreSQL ограничения

3. Реализовать процесс миграции:
   - Создать скрипты для миграции схемы
   - Реализовать откат миграций
   - Добавить проверки целостности данных

#### Ожидаемый результат:
- Все таблицы успешно созданы в PostgreSQL
- Миграции работают корректно
- Схема данных оптимизирована для PostgreSQL

### 3.3 Этап 3: Интеграция TimescaleDB (День 5-6)

#### Задачи для агента Qoder:
1. Настроить TimescaleDB расширение:
   - Проверить установку TimescaleDB
   - Создать hypertables для временных рядов
   - Настроить партиционирование

2. Оптимизировать таблицы для временных рядов:
   - Преобразовать `calculation_data` в hypertable
   - Преобразовать `forecasts` в hypertable
   - Преобразовать `analytics` в hypertable

3. Реализовать специфичные функции TimescaleDB:
   - _continuous aggregates_ для аналитики
   - _compression policies_ для старых данных
   - _retention policies_ для архивации

#### Ожидаемый результат:
- TimescaleDB полностью интегрирован
- Временные ряды оптимизированы
- Реализованы политики сжатия и хранения

### 3.4 Этап 4: Оптимизация производительности (День 7-8)

#### Задачи для агента Qoder:
1. Оптимизировать индексы:
   - Создать составные индексы для частых запросов
   - Добавить частичные индексы
   - Реализовать функциональные индексы

2. Настроить пул соединений:
   - Оптимизировать параметры пула
   - Реализовать мониторинг соединений
   - Добавить логирование проблем с соединениями

3. Реализовать кэширование:
   - Добавить кэширование часто запрашиваемых данных
   - Реализовать инвалидацию кэша
   - Настроить TTL для кэшированных данных

#### Ожидаемый результат:
- Значительно улучшена производительность запросов
- Оптимизировано использование соединений
- Реализовано эффективное кэширование

### 3.5 Этап 5: Тестирование и валидация (День 9-10)

#### Задачи для агента Qoder:
1. Создать тесты для PostgreSQL:
   - Модульные тесты для всех моделей
   - Интеграционные тесты для сервисов
   - Тесты производительности

2. Провести миграцию тестовых данных:
   - Создать тестовые наборы данных
   - Проверить целостность данных после миграции
   - Валидировать результаты расчетов

3. Оптимизировать на основе результатов тестирования:
   - Профилировать медленные запросы
   - Оптимизировать планы выполнения
   - Улучшить индексы на основе реальных запросов

#### Ожидаемый результат:
- Все тесты проходят успешно
- Данные мигрируют без потерь
- Производительность соответствует требованиям

## 4. Подробные задачи для агента Qoder

### 4.1 Задача: Обновление конфигурации базы данных
**Файл:** `src/core/database/database.py`

**Изменения:**
1. Обновить `get_database_url()` для поддержки PostgreSQL:
   ```python
   def get_database_url():
       """
       Получает URL для подключения к базе данных PostgreSQL.
       """
       # Получить параметры из переменных окружения
       db_host = os.getenv('DB_HOST', 'localhost')
       db_port = os.getenv('DB_PORT', '5432')
       db_name = os.getenv('DB_NAME', 'shrinkage_db')
       db_user = os.getenv('DB_USER', 'shrinkage_user')
       db_password = os.getenv('DB_PASSWORD', 'shrinkage_password')
       
       return f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
   ```

2. Обновить `create_database_engine()` для оптимизации PostgreSQL:
   ```python
   def create_database_engine():
       """
       Создает движок базы данных PostgreSQL с оптимизированными параметрами.
       """
       try:
           database_url = get_database_url()
           log.info(f"Создание подключения к PostgreSQL: {database_url}")
           
           engine = create_engine(
               database_url,
               pool_size=20,
               max_overflow=30,
               pool_pre_ping=True,
               pool_recycle=3600,
               echo=False
           )
           
           return engine
       except Exception as e:
           log.error(f"Ошибка при создании подключения к PostgreSQL: {e}")
           raise
   ```

### 4.2 Задача: Создание конфигурационного файла
**Файл:** `src/core/database/config.py`

**Содержимое:**
```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Конфигурация базы данных для системы расчета коэффициентов усушки.
"""

import os
from src.logger_config import log

class DatabaseConfig:
    """Конфигурация базы данных."""
    
    # Параметры подключения к PostgreSQL
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '5432')
    DB_NAME = os.getenv('DB_NAME', 'shrinkage_db')
    DB_USER = os.getenv('DB_USER', 'shrinkage_user')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'shrinkage_password')
    
    # Параметры пула соединений
    POOL_SIZE = int(os.getenv('POOL_SIZE', '20'))
    MAX_OVERFLOW = int(os.getenv('MAX_OVERFLOW', '30'))
    POOL_RECYCLE = int(os.getenv('POOL_RECYCLE', '3600'))
    POOL_PRE_PING = os.getenv('POOL_PRE_PING', 'true').lower() == 'true'
    
    # Параметры TimescaleDB
    TIMESCALEDB_ENABLED = os.getenv('TIMESCALEDB_ENABLED', 'true').lower() == 'true'
    
    @classmethod
    def get_database_url(cls):
        """Получает URL для подключения к базе данных."""
        return f"postgresql://{cls.DB_USER}:{cls.DB_PASSWORD}@{cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_NAME}"
    
    @classmethod
    def validate_config(cls):
        """Проверяет конфигурацию базы данных."""
        required_vars = ['DB_HOST', 'DB_PORT', 'DB_NAME', 'DB_USER', 'DB_PASSWORD']
        missing_vars = []
        
        for var in required_vars:
            if not getattr(cls, var):
                missing_vars.append(var)
        
        if missing_vars:
            log.warning(f"Отсутствуют обязательные переменные окружения: {missing_vars}")
            return False
        
        return True
```

### 4.3 Задача: Адаптация моделей для PostgreSQL
**Файл:** `src/core/database/models.py`

**Изменения:**
1. Добавить поддержку TimescaleDB:
   ```python
   # Добавить после определения классов моделей
   if DatabaseConfig.TIMESCALEDB_ENABLED:
       # Преобразовать таблицы временных рядов в hypertables
       # Это будет реализовано через миграции Alembic
       pass
   ```

2. Оптимизировать индексы:
   ```python
   # Пример оптимизации для CalculationData
   class CalculationData(Base):
       __tablename__ = 'calculation_data'
       
       # Существующие поля...
       
       # Добавить составные индексы
       __table_args__ = (
           Index('idx_calc_data_nomenclature_date', 'nomenclature_id', 'calculation_date'),
           Index('idx_calc_data_period', 'inventory_period_start', 'inventory_period_end'),
           Index('idx_calc_data_quality', 'data_quality_flag'),
       )
   ```

### 4.4 Задача: Создание миграций Alembic
**Каталог:** `src/core/database/alembic/versions/`

**Новая миграция:** `004_postgresql_optimization.py`

**Содержимое:**
````
"""PostgreSQL optimization and TimescaleDB integration

Revision ID: 004
Revises: 003
Create Date: 2024-01-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

# revision identifiers
revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None

def upgrade():
    # Создать hypertables для временных рядов
    op.execute("CREATE EXTENSION IF NOT EXISTS timescaledb")
    
    # Преобразовать таблицы в hypertables
    op.execute("SELECT create_hypertable('calculation_data', 'calculation_date', if_not_exists => TRUE)")
    op.execute("SELECT create_hypertable('forecasts', 'forecast_date', if_not_exists => TRUE)")
    op.execute("SELECT create_hypertable('analytics', 'last_updated', if_not_exists => TRUE)")
    
    # Оптимизировать типы данных
    op.alter_column('calculation_data', 'fifo_batch_sequence', type_=JSONB)
    op.alter_column('preliminary_forecasts', 'batch_storage_history', type_=JSONB)
    op.alter_column('surplus_recommendations', 'supporting_data', type_=JSONB)
    op.alter_column('ai_patterns', 'pattern_data', type_=JSONB)
    op.alter_column('ml_model_registry', 'parameters', type_=JSONB)
    op.alter_column('ml_model_registry', 'accuracy_metrics', type_=JSONB)

def downgrade():
    # Откатить изменения
    op.alter_column('ml_model_registry', 'accuracy_metrics', type_=sa.JSON)
    op.alter_column('ml_model_registry', 'parameters', type_=sa.JSON)
    op.alter_column('ai_patterns', 'pattern_data', type_=sa.JSON)
    op.alter_column('surplus_recommendations', 'supporting_data', type_=sa.JSON)
    op.alter_column('preliminary_forecasts', 'batch_storage_history', type_=sa.JSON)
    op.alter_column('calculation_data', 'fifo_batch_sequence', type_=sa.JSON)