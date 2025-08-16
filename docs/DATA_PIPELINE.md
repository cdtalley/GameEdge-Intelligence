# Data Pipeline Documentation

## Overview

The GameEdge Intelligence platform includes a comprehensive data pipeline that transforms real-world datasets into sports betting analytics data. This pipeline handles downloading, transformation, and loading of three primary datasets to create a realistic sports betting environment for analysis and machine learning.

## Datasets

### 1. Sentiment140 (Twitter Sentiment Analysis)
- **Source**: [Kaggle - Sentiment140](https://www.kaggle.com/datasets/kazanova/sentiment140)
- **Size**: ~80 MB
- **Records**: 1.6M+ pre-labeled tweets
- **Purpose**: Sentiment analysis training and customer feedback simulation
- **Transformation**: Twitter sentiment → Betting platform reviews and interactions

### 2. Online Retail II UCI (Customer Behavior)
- **Source**: [Kaggle - Online Retail II UCI](https://www.kaggle.com/datasets/mashlyn/online-retail-ii-uci)
- **Size**: ~45 MB
- **Records**: 525K+ transaction records
- **Purpose**: Customer behavior modeling and RFM analysis
- **Transformation**: Retail customers → Sports betting customers, purchases → bets

### 3. Beat The Bookie Football Dataset (Sports Betting)
- **Source**: [Kaggle - Beat The Bookie](https://www.kaggle.com/datasets/austro/beat-the-bookie-worldwide-football-dataset)
- **Size**: ~120 MB
- **Records**: 500K+ sports matches with odds
- **Purpose**: Real sports betting data and odds analysis
- **Transformation**: Football odds → Betting transactions and game data

## Data Transformation Process

### Phase 1: Data Download
```bash
# Download all datasets
python scripts/manage_data_pipeline.py download --kaggle-token "username:key"

# Download specific dataset
python scripts/manage_data_pipeline.py download --kaggle-token "username:key" --datasets sentiment140
```

### Phase 2: Data Transformation

#### Sentiment140 → Betting Interactions
- **Input**: Twitter sentiment data (positive/negative)
- **Output**: Customer reviews and feedback
- **Process**:
  - Map sentiment labels to betting context
  - Generate realistic betting-related text
  - Create interaction records with sentiment analysis
  - Assign to random users for realistic distribution

#### Online Retail → Users & Bets
- **Input**: Customer purchase history
- **Output**: Betting customers and transactions
- **Process**:
  - Aggregate customer behavior (RFM metrics)
  - Create user profiles with betting preferences
  - Transform purchases into betting transactions
  - Generate realistic betting patterns and outcomes

#### Football Odds → Sports Bets
- **Input**: Historical football match data
- **Output**: Sports betting transactions
- **Process**:
  - Map team names and match data
  - Generate realistic betting stakes and outcomes
  - Create diverse betting types and sports
  - Maintain historical accuracy of match dates

### Phase 3: Data Loading
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Tables**: Users, Bets, Interactions, Segments
- **Relationships**: Maintain referential integrity
- **Batch Processing**: Efficient bulk inserts for large datasets

## Usage

### Command Line Interface

The data pipeline can be managed through the `manage_data_pipeline.py` script:

```bash
# Check current status
python scripts/manage_data_pipeline.py status

# Download datasets
python scripts/manage_data_pipeline.py download --kaggle-token "username:key"

# Transform downloaded data
python scripts/manage_data_pipeline.py transform

# Generate synthetic data for testing
python scripts/manage_data_pipeline.py synthetic --num-users 1000

# Run complete pipeline
python scripts/manage_data_pipeline.py run-all --kaggle-token "username:key"

# Clean up all data
python scripts/manage_data_pipeline.py cleanup
```

### API Endpoints

The data pipeline is also accessible through REST API endpoints:

```bash
# Check pipeline status
GET /api/v1/data-pipeline/status

# Run full pipeline
POST /api/v1/data-pipeline/pipeline/run
{
    "kaggle_token": "username:key"
}

# Generate synthetic data
POST /api/v1/data-pipeline/pipeline/synthetic
{
    "num_users": 1000
}

# Transform specific dataset
POST /api/v1/data-pipeline/pipeline/transform/sentiment140

# Get pipeline information
GET /api/v1/data-pipeline/pipeline/info
```

## Configuration

### Environment Variables

```bash
# Data pipeline configuration
DATA_DIR=./data

# Kaggle API credentials (set in ~/.kaggle/kaggle.json)
KAGGLE_USERNAME=your_username
KAGGLE_KEY=your_api_key
```

### Kaggle Setup

1. **Create Kaggle Account**: Sign up at [kaggle.com](https://kaggle.com)
2. **Generate API Token**: Go to Account → API → Create New API Token
3. **Download kaggle.json**: Save the token file
4. **Install Kaggle CLI**: `pip install kaggle`
5. **Set Credentials**: Place `kaggle.json` in `~/.kaggle/` directory

## Data Quality & Validation

### Transformation Rules
- **User IDs**: Maintain consistency across related records
- **Timestamps**: Preserve temporal relationships
- **Financial Data**: Realistic betting amounts and payouts
- **Sentiment Scores**: Calibrated confidence levels
- **Sports Mapping**: Consistent categorization

### Data Validation
- **Referential Integrity**: All foreign keys reference valid records
- **Data Types**: Proper column types and constraints
- **Range Validation**: Realistic values for betting amounts, odds, etc.
- **Completeness**: Required fields populated for all records

## Performance Considerations

### Large Dataset Handling
- **Batch Processing**: Process records in chunks
- **Progress Tracking**: Visual progress bars for long operations
- **Memory Management**: Efficient pandas operations
- **Database Optimization**: Bulk inserts and proper indexing

### Scalability
- **Async Operations**: Non-blocking dataset downloads
- **Background Tasks**: Long-running operations don't block API
- **Resource Monitoring**: Track memory and CPU usage
- **Error Recovery**: Graceful handling of failures

## Monitoring & Logging

### Pipeline Status
```bash
# Check download status
python scripts/manage_data_pipeline.py status

# Monitor API endpoints
curl /api/v1/data-pipeline/status
```

### Log Files
- **Application Logs**: Structured logging with structlog
- **Pipeline Logs**: Detailed transformation progress
- **Error Logs**: Failed operations and recovery steps
- **Performance Logs**: Timing and resource usage

## Troubleshooting

### Common Issues

#### Dataset Download Failures
```bash
# Check Kaggle credentials
cat ~/.kaggle/kaggle.json

# Verify API token validity
kaggle datasets list

# Check network connectivity
ping kaggle.com
```

#### Transformation Errors
```bash
# Check file permissions
ls -la data/

# Verify CSV format
head -5 data/sentiment140.csv

# Check database connectivity
python -c "from app.core.database import engine; print(engine)"
```

#### Memory Issues
```bash
# Monitor memory usage
htop

# Process smaller batches
python scripts/manage_data_pipeline.py transform --datasets sentiment140
```

### Recovery Procedures

#### Partial Failures
1. **Identify Failed Step**: Check logs for specific error
2. **Clean Partial Data**: Remove incomplete records
3. **Restart Pipeline**: Resume from failed step
4. **Verify Results**: Check data integrity

#### Database Issues
1. **Check Connections**: Verify database accessibility
2. **Review Logs**: Identify specific error messages
3. **Restart Services**: Restart PostgreSQL if needed
4. **Restore Data**: Use backup if corruption detected

## Best Practices

### Development
- **Test with Small Datasets**: Use subset of data for development
- **Validate Transformations**: Verify output quality
- **Monitor Performance**: Track processing times
- **Version Control**: Track pipeline changes

### Production
- **Backup Before Changes**: Always backup existing data
- **Test in Staging**: Validate pipeline in test environment
- **Monitor Resources**: Track CPU, memory, and disk usage
- **Alert on Failures**: Set up monitoring and alerting

### Data Management
- **Regular Updates**: Keep datasets current
- **Archive Old Data**: Maintain historical records
- **Data Lineage**: Track data transformations
- **Quality Metrics**: Monitor data quality over time

## Future Enhancements

### Planned Features
- **Real-time Streaming**: Live data ingestion
- **Additional Datasets**: More sports and betting data
- **Advanced Transformations**: ML-powered data enhancement
- **Data Versioning**: Track dataset versions and changes
- **Automated Scheduling**: Cron-based pipeline execution

### Integration Opportunities
- **External APIs**: Live sports data feeds
- **Social Media**: Real-time sentiment analysis
- **Market Data**: Live odds and betting lines
- **User Analytics**: Behavioral tracking and analysis

## Support & Resources

### Documentation
- **API Docs**: `/docs` endpoint for interactive documentation
- **Code Comments**: Inline documentation in source code
- **Examples**: Sample data and transformation scripts

### Community
- **GitHub Issues**: Report bugs and request features
- **Discussions**: Community support and ideas
- **Contributions**: Pull requests and improvements welcome

### Contact
- **Development Team**: GameEdge Intelligence Platform
- **Repository**: [GitHub Repository URL]
- **Documentation**: [Documentation URL]
