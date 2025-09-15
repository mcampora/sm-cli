# SageMaker Unified Studio CLI

A command-line interface (CLI) tool to simplify the creation and management of AWS resources.  
You can create a data mesh with a central governance account and 3 development accounts (dev, test, prod).  
Ultimately the goal of this POC is to illustrate how to manage the lifecycle of a given pipeline (from development to production). 

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

- **List Domains**
  List all SageMaker domains in the current region.
  ```bash
  sm-cli list-domains
  ```

- **Describe Domain**
  Show detailed information about a specific domain.
  ```bash
  sm-cli describe-domain --domain-id <domain_id>
  ```

- **Create Domain**
  Create a new SageMaker domain.
  ```bash
  sm-cli create-domain --config-file <config_file>
  ```

- **Delete Domain**
  Delete an existing SageMaker domain.
  ```bash
  sm-cli delete-domain --domain-id <domain_id>
  ```

### Account Management

- **List Accounts**
  List all accounts in the organization.
  ```bash
  sm-cli list-accounts
  ```

- **Invite Account**
  Invite an AWS account to the organization.
  ```bash
  sm-cli invite-account --account-id <account_id> --email <email>
  ```

- **Uninvite Account**
  Remove an account invitation.
  ```bash
  sm-cli uninvite-account --account-id <account_id>
  ```

### Project Management

- **List Projects**
  List all projects in a domain.
  ```bash
  sm-cli list-projects --domain-id <domain_id>
  ```

- **Create Project**
  Create a new project.
  ```bash
  sm-cli create-project --domain-id <domain_id> --project-name <name> --template <template_file>
  ```

- **Delete Project**
  Delete a project.
  ```bash
  sm-cli delete-project --domain-id <domain_id> --project-name <name>
  ```

### Blueprint Management

- **List Blueprints**
  List all available blueprints.
  ```bash
  sm-cli list-blueprints
  ```

- **Describe Blueprint**
  Display detailed information about a specific blueprint configuration.
  ```bash
  sm-cli describe-blueprint --blueprint-name <name>
  ```

### Utility Commands

- **Status**
  Show the current status of the CLI and AWS configuration.
  ```bash
  sm-cli status
  ```

- **Help**
  Show help message and usage information.
  ```bash
  sm-cli --help
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

## Current limitations or required improvements
- delete-project command returns immediately, the project deletion can take up to 5 minutes. You cannot use the uninvite-account or delete-domain commands until the project is deleted.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
