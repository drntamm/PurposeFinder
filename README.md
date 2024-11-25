# Purpose Finder

A web application that helps individuals discover their life purpose by combining the ancient Japanese concept of Ikigai with biblical spiritual gifts assessment.

## Features

- Multi-step assessment process
- Integration of Ikigai's four elements:
  - What you love
  - What you're good at
  - What the world needs
  - What you can be paid for
- Spiritual gifts assessment based on biblical principles
- Beautiful, modern UI with smooth transitions
- Personalized results and recommendations

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd PurposeFinder
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
python app.py
```

5. Open your browser and navigate to `http://localhost:5000`

## Project Structure

```
PurposeFinder/
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── static/
│   └── css/
│       └── style.css  # Custom styles
├── templates/
│   ├── base.html      # Base template
│   ├── index.html     # Home page
│   └── assessment.html # Assessment form
└── README.md
```

## Contributing

1. Fork the repository
2. Create a new branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
