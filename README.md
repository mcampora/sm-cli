# SageMaker Unified Studio CLI

A command-line interface (CLI) tool to simplify the creation and management of AWS resources.

## Features

- Simple CLI interface for AWS resource management
- Secure credential handling using a local credentials file

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

1. Open the credentials file and update it with your AWS credentials:
   ```bash
   [default]
   aws_access_key_id=...
   aws_secret_access_key=...
   aws_session_token=...
   ```
   You need to at least define the default profile.  
   3 additional profiles are available to create a data mesh with 4 accounts:
   - dev
   - test
   - prod

## Available Commands

### Domain Management

- **List all domains**
List all the available domains in the default (governance) account.  
  ```bash
  sm list-domains
  ```

- **Describe a specific domain**
Dumps the details of a specific domain as a JSON document.  
  ```bash
  sm describe-domain --name your-domain
  # or
  sm describe-domain --domain-id dzd_xxxxxxxxx
  ```

- **Create a new domain**
Create a new domain from a manifest file, an example is available in the main folder.
  ```bash
  sm create-domain --manifest domain.json
  ```

- **Delete a domain**
Delete a domain and its resources, use with caution as it will delete all assets, projects, project profiles. accounts associations.
  ```bash
  sm delete-domain --name your-domain
  # or with force flag (no confirmation)
  sm delete-domain --name your-domain --force
  ```

### Account Management

- **List accounts associated with a domain**
List all the accounts associated with a given domain.
  ```bash
  sm list-accounts --domain-name your-domain
  # or
  sm list-accounts --domain-id dzd_xxxxxxxxx
  ```

- **Invite an AWS account to a domain**
Invite an AWS account to a domain, creates a project profile for the account (ex. CustomProfile_dev).
  ```bash
  sm invite-account --domain-name your-domain --account dev
  ```

- **Uninvite an AWS account from a domain**
Remove an AWS account from a domain, use with caution as it will delete all assets, projects, the project profile and account association.
  ```bash
  sm uninvite-account --domain-name your-domain --account dev
  ```

### Project Management

- **List all projects in a domain**
List all the projects associated with a given domain. Dumps the details as a JSON document.  
  ```bash
  sm list-projects --domain-name your-domain
  # or
  sm list-projects --domain-id dzd_xxxxxxxxx
  ```

- **Create a new project**
Create a new project in a domain from a manifest file, an example is available in the main folder.
  ```bash
  sm create-project --domain-name your-domain --manifest project.json --account dev
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
  sm status --account dev
  ```

## Configuration

The tool uses the AWS credentials file (default location: `./credentials`). You can specify different profiles using the `--account` flag with any command.

Check AWS connection status:
```bash
sm status
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
