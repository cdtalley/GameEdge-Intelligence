# GameEdge Intelligence - Sports Betting Analytics Platform

A comprehensive sentiment analysis and customer segmentation platform for sports betting and fantasy sports, built with enterprise-grade architecture and advanced ML capabilities.

## 🚀 Features

- **Sentiment Analysis Engine**: Multi-model approach with BERT-based transformers and traditional ML fallback
- **Customer Segmentation System**: RFM analysis, clustering algorithms, churn prediction
- **Real-time Analytics**: Live sentiment monitoring and customer behavior tracking
- **Advanced ML Pipeline**: Automated training, feature engineering, and model monitoring
- **Modern UI/UX**: Dark theme with sports betting aesthetic, responsive design
- **Production Ready**: Docker containers, environment configs, CI/CD ready

## 🛠️ Tech Stack

- **Frontend**: Next.js 14 (App Router), TypeScript, Tailwind CSS, Shadcn/ui
- **Backend**: Python FastAPI with async capabilities
- **ML/Data**: scikit-learn, transformers (Hugging Face), pandas, numpy
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Visualization**: Recharts, D3.js for advanced charts
- **Real-time**: WebSockets for live updates
- **Deployment**: Docker containers, environment configs

## 📊 Dataset Scale

- **1.6 million pre-labeled tweets** for sentiment analysis training
- **525k+ real transaction records** for customer behavior modeling
- **500k+ sports matches** with comprehensive odds data
- **50k+ synthetic customer profiles** with realistic demographics
- **100k+ simulated betting transactions** across multiple sports
- **25k+ generated customer reviews** and feedback texts

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 18+
- Docker and Docker Compose
- PostgreSQL

### 1. Clone and Setup
```bash
git clone <repository-url>
cd gameedge-intelligence
```

### 2. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Frontend Setup
```bash
cd frontend
npm install
```

### 4. Database Setup
```bash
# Using Docker
docker-compose up -d postgres
```

### 5. Environment Configuration
```bash
# Copy and configure environment files
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```

### 6. Data Pipeline Setup (Optional)
```bash
# Install Kaggle CLI for dataset downloads
pip install kaggle

# Check pipeline status
python scripts/manage_data_pipeline.py status

# Generate synthetic data for testing
python scripts/manage_data_pipeline.py synthetic --num-users 1000

# Download and transform real datasets (requires Kaggle token)
python scripts/manage_data_pipeline.py run-all --kaggle-token "username:key"
```

### 7. Run Development Servers
```bash
# Backend (from backend directory)
uvicorn main:app --reload

# Frontend (from frontend directory)
npm run dev
```

## 📁 Project Structure

```
gameedge-intelligence/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API endpoints
│   │   ├── core/           # Core configuration
│   │   ├── models/         # Database models
│   │   ├── services/       # Business logic
│   │   └── ml/             # ML models and pipelines
│   ├── requirements.txt
│   └── main.py
├── frontend/                # Next.js frontend
│   ├── app/                # App Router pages
│   ├── components/         # Reusable components
│   ├── lib/                # Utilities and helpers
│   └── package.json
├── docker-compose.yml       # Development environment
├── scripts/                 # Management scripts
│   ├── manage_data_pipeline.py  # Data pipeline CLI
│   ├── test_data_pipeline.py    # Pipeline testing
│   ├── quick-start.sh           # Environment setup
│   └── stop-services.sh         # Service management
├── .github/                 # CI/CD workflows
└── docs/                    # Documentation
```

## 🔧 Development

### Backend Development
- FastAPI with automatic API documentation
- SQLAlchemy ORM with PostgreSQL
- Async processing for ML operations
- Comprehensive testing with pytest

### Frontend Development
- Next.js 14 with App Router
- TypeScript for type safety
- Tailwind CSS for styling
- Shadcn/ui components
- Real-time updates with WebSockets

### ML Pipeline
- Automated data preprocessing
- Model training and validation
- Real-time inference API
- Performance monitoring and drift detection

## 📈 API Endpoints

### Core APIs
- `POST /api/v1/sentiment/analyze` - Analyze text sentiment
- `GET /api/v1/customers/segments` - Get customer segments
- `POST /api/v1/customers/segment` - Create new segment
- `GET /api/v1/analytics/dashboard` - Dashboard metrics
- `GET /api/v1/predictions/churn` - Churn predictions

### Data Pipeline APIs
- `GET /api/v1/data-pipeline/status` - Check pipeline status
- `POST /api/v1/data-pipeline/pipeline/run` - Run full data pipeline
- `POST /api/v1/data-pipeline/pipeline/synthetic` - Generate synthetic data
- `POST /api/v1/data-pipeline/pipeline/transform/{dataset}` - Transform specific dataset
- `GET /api/v1/data-pipeline/pipeline/info` - Get pipeline information

### Real-time Features
- `WebSocket /ws/live-sentiment` - Real-time sentiment feed

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm run test
```

## 🚀 Deployment

### Docker Production Build
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Environment Variables
- `DATABASE_URL` - PostgreSQL connection string
- `JWT_SECRET` - JWT signing secret
- `ML_MODEL_PATH` - Path to trained ML models
- `REDIS_URL` - Redis connection for caching

## 📚 Documentation

- [API Documentation](./docs/api.md)
- [Data Pipeline Guide](./docs/DATA_PIPELINE.md)
- [ML Pipeline Guide](./docs/ml-pipeline.md)
- [Deployment Guide](./docs/deployment.md)
- [Contributing Guidelines](./docs/contributing.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the documentation
- Review the troubleshooting guide

---

**GameEdge Intelligence** - Transforming sports betting through AI-powered analytics and customer intelligence.
