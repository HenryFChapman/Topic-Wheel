# Topic Wheel

A web application that generates and displays topic wheels for various subjects. The application uses Python for backend processing and HTML/CSS for the frontend visualization.

## Features

- Generates topic wheels from JSON data
- Interactive web interface
- Customizable topic visualization
- Easy-to-use setup process

## Prerequisites

- Python 3.x
- pip (Python package installer)

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd Topic-Wheel
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

3. Install the required dependencies:
```bash
pip install -r requirements.txt
```

4. Set up your API key:
   - Create a file named `api_key.txt` in the root directory
   - Add your API key to the file

## Usage

1. Run the setup script:
```bash
./setup.sh
```

2. Open `index.html` in your web browser to view the topic wheel.

## Project Structure

- `get_topics.py`: Python script for fetching and processing topic data
- `topics_data.json`: JSON file containing topic data
- `index.html`: Main web interface
- `setup.sh`: Setup script for the project
- `requirements.txt`: Python dependencies
- `api_key.txt`: API key file (not tracked in git)

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Thanks to all contributors who have helped shape this project
- Special thanks to the open-source community for their valuable tools and libraries 