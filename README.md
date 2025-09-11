# SMUS Setup

A command-line interface (CLI) tool to simplify the creation and management of AWS resources.

## Features

- Simple CLI interface for AWS resource management
- Secure credential handling using environment variables
- Easy to extend with new AWS resource types

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/smus-setup.git
   cd smus-setup
   ```

2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the package in development mode:
   ```bash
   pip install -e .
   ```

## Configuration

1. Copy the example environment file and update with your AWS credentials:
   ```bash
   cp .env.example .env
   ```

2. Edit the `.env` file and add your AWS credentials:
   ```
   AWS_ACCESS_KEY_ID=your_access_key_here
   AWS_SECRET_ACCESS_KEY=your_secret_key_here
   AWS_DEFAULT_REGION=us-east-1
   ```

## Usage

Show help:
```bash
smus --help
```

Check AWS connection status:
```bash
smus status
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
