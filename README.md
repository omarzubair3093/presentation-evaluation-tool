# 📊 Presentation Evaluation Tool

AI-powered presentation evaluation using Claude API with persistent storage and comprehensive reporting.

## Features

- 🎯 **Automated Evaluation**: Uses Claude Sonnet 4 to analyze presentations
- 💾 **Persistent Storage**: SQLite database stores all evaluations permanently
- 📈 **Dashboard**: View statistics, scores, and cost tracking
- 📄 **PDF Reports**: Download detailed evaluation reports
- ⚙️ **Customizable Rubric**: Adjust evaluation criteria and weights
- 💰 **Cost Tracking**: Monitor API usage costs per evaluation
- 🌍 **Language Support**: Generates English reports for any input language

## Quick Start

### 1. Local Development

```bash
# Clone or download this repository
cd pres-eval-tool

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export ANTHROPIC_API_KEY="your-api-key"
export SECRET_KEY="any-random-string"

# Run the application
python app.py
```

Visit: http://localhost:5000

### 2. Deploy to Render (Recommended)

See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for detailed instructions.

**Quick steps:**
1. Get Anthropic API key from console.anthropic.com
2. Push code to GitHub
3. Connect to Render.com
4. Add environment variables
5. Deploy!

## Evaluation Rubric

Default evaluation dimensions (customizable):

| Dimension | Weight | Description |
|-----------|--------|-------------|
| User Input Quality | 15% | Quality of provided content |
| System Understanding | 20% | AI comprehension of task |
| Content Accuracy | 25% | Data extraction accuracy |
| Content Structure | 15% | Narrative flow and organization |
| Design Quality | 15% | Visual design execution |
| Instruction Adherence | 10% | Following user requirements |

## Usage

### Evaluate a Presentation

1. Go to "New Evaluation" tab
2. Upload:
   - JSON file (presentation metadata)
   - PDF file (generated presentation)
   - Additional files (optional)
3. Click "Evaluate Presentation"
4. Wait 30-60 seconds
5. View results and download report

### View Past Evaluations

- Click "Evaluated Presentations" tab
- See all evaluations with scores, categories, and costs
- Download individual reports as PDFs

### Customize Rubric

- Click "Rubric Settings" tab
- Adjust dimension weights (must total 100%)
- Save changes for future evaluations

## Cost Structure

- **Per Evaluation**: ~$0.01 - $0.05
- **Free Tier**: Anthropic provides $5 credit (100-500 evaluations)
- **Tracking**: Real-time cost display in dashboard and per-evaluation

## Tech Stack

- **Backend**: Flask (Python)
- **AI**: Anthropic Claude Sonnet 4
- **Database**: SQLite3 (with persistent disk option)
- **PDF Generation**: ReportLab
- **Deployment**: Render.com / Railway.app
- **Frontend**: Vanilla JavaScript (no frameworks)

## File Structure

```
pres-eval-tool/
├── app.py                  # Main Flask application
├── requirements.txt        # Python dependencies
├── Procfile               # Deployment configuration
├── runtime.txt            # Python version
├── DEPLOYMENT_GUIDE.md    # Detailed deployment instructions
├── templates/
│   └── index.html         # Web interface
└── uploads/               # Uploaded files (auto-created)
```

## Environment Variables

Required:
- `ANTHROPIC_API_KEY`: Your Anthropic API key
- `SECRET_KEY`: Flask secret key (any random string)

Optional:
- `PORT`: Server port (default: 5000)

## Database Schema

### evaluations
- id, user_outline, user_preferences
- presentation_link, overall_score, score_category
- doc_type, report_path, json_data
- cost_usd, input_tokens, output_tokens
- created_at, scores_json

### rubric
- id, dimension, weight, description

## API Endpoints

- `GET /` - Main dashboard
- `GET /api/evaluations` - List all evaluations
- `GET /api/rubric` - Get rubric configuration
- `POST /api/rubric` - Update rubric
- `POST /api/evaluate` - Submit new evaluation
- `GET /api/report/<id>` - Download report PDF
- `GET /api/stats` - Get usage statistics

## Security

- API keys stored as environment variables (never in code)
- File uploads validated and secured
- Session management with Flask secrets
- SQL injection protection via parameterized queries

## Limitations

- Max file size: 50MB
- SQLite suitable for 1-10 users concurrent
- Free hosting has cold starts (~30s first load)
- Render free tier: 750 hours/month

## Scaling

For production use with >10 concurrent users:
- Upgrade to PostgreSQL
- Use Redis for caching
- Deploy to paid hosting tier
- Add authentication system

## Contributing

This is a self-contained tool. For improvements:
1. Modify code locally
2. Test thoroughly
3. Push to GitHub
4. Redeploy to Render

## License

MIT License - Use freely for personal or commercial projects

## Support

- Check DEPLOYMENT_GUIDE.md for detailed help
- Review Render logs for deployment issues
- Test locally first to isolate problems

## Version

1.0.0 - Initial release

---

**Built with ❤️ using Claude and ReportLab**
