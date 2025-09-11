# SMUS Setup

A command-line interface (CLI) tool to simplify the creation and management of AWS resources.

## Features

- Simple CLI interface for AWS resource management
- Secure credential handling using environment variables
- Easy to extend with new AWS resource types

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/sm-setup.git
   cd sm-setup
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

1. Open the credentials file and update itwith your AWS credentials:
   ```bash
   [default]
   aws_access_key_id=...
   aws_secret_access_key=...
   aws_session_token=...
   ```
   You need to at least define the default profile.  
   3 additional profiles are available to create a data mesh with 4 accounts:
   - governance
   - dev
   - test
   - prod

## Available Commands

### Domain Management

- **List all domains**
  ```bash
  sm list-domains
  ```

- **Describe a specific domain**
  ```bash
  sm describe-domain --name your-domain
  # or
  sm describe-domain --domain-id dzd_xxxxxxxxx
  ```

- **Create a new domain**
  ```bash
  sm create-domain --manifest domain-manifest.json
  ```

- **Delete a domain**
  ```bash
  sm delete-domain --name your-domain
  # or with force flag (no confirmation)
  sm delete-domain --name your-domain --force
  ```

### Account Management

- **List accounts associated with a domain**
  ```bash
  sm list-accounts --domain-name your-domain
  # or
  sm list-accounts --domain-id dzd_xxxxxxxxx
  ```

- **Invite an AWS account to a domain**
  ```bash
  sm invite-account --domain-name your-domain --account-id 123456789012
  ```

- **Uninvite an AWS account from a domain**
  ```bash
  sm uninvite-account --domain-name your-domain --account-id 123456789012
  ```

### Project Management

- **List all projects in a domain**
  ```bash
  sm list-projects --domain-name your-domain
  # or
  sm list-projects --domain-id dzd_xxxxxxxxx
  ```

- **Create a new project**
  ```bash
  sm create-project --domain-name your-domain --name my-project --environment dev
  # With description and custom profile
  sm create-project --domain-id dzd_xxxxxxxxx --name my-project --environment test --description "Test project" --profile your-profile
  ```

### Utility Commands

- **Show help**
  ```bash
  sm --help
  # or
  sm help
  ```

- **Check AWS connection status**
  ```bash
  sm status
  # With custom profile
  sm status --profile your-profile
  ```

## Configuration

The tool uses the AWS credentials file (default location: `./credentials`). You can specify different profiles using the `--profile` flag with any command.

Check AWS connection status:
```bash
sm status
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
