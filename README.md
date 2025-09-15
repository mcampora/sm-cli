# SageMaker Unified Studio CLI

A command-line interface (CLI) tool to simplify the creation and management of AWS resources.  

I was able to create a domain, invite accounts to this domain (ie. dev, test, prod), activate blueprints in these accounts, discover the settings coming with these blueprints, create a project profile with custom settings (ex. the GitHub organization), create projects with custom parameters (ex. the associated GitHub repo).

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
  sm list-domains
  ```

- **Describe Domain**
  Show detailed information about a specific domain.
  ```bash
  sm describe-domain --domain-name <domain_name>
  ```

- **Create Domain**
  Create a new SageMaker domain.
  ```bash
  sm create-domain --manifest <config_file>
  ```

- **Delete Domain**
  Delete an existing SageMaker domain.
  ```bash
  sm delete-domain --domain-name <domain_name> --force
  ```

### Account Management

- **List Accounts**
  List all accounts in the organization.
  ```bash
  sm list-accounts
  ```

- **Invite Account**
  Invite an AWS account to the organization.
  ```bash
  sm invite-account --domain-name <domain_name> --account <profiel_namne>
  ```

- **Uninvite Account**
  Remove an account invitation.
  ```bash
  sm uninvite-account --domain-name <domain_name> --account <profile_name>
  ```

### Project Management

- **List Projects**
  List all projects in a domain.
  ```bash
  sm list-projects --domain-name <domain_name>
  ```

- **Create Project**
  Create a new project.
  ```bash
  sm create-project --domain-name <domain_name> --name <name> --account <profile_name>
  ```

- **Delete Project**
  Delete a project.
  ```bash
  sm delete-project --domain-name <domain_name> --name <name> --force
  ```

### Blueprint Management

- **List Blueprints**
  List all available blueprints.
  ```bash
  sm list-blueprints --domain-name <domain_name>
  ```

- **Describe Blueprint**
  Display detailed information about a specific blueprint configuration.
  ```bash
  sm describe-blueprint --domain-name <domain_name> --name <blueprint_name>
  ```

### Utility Commands

- **Status**
  Show the current status of the CLI and AWS configuration.
  ```bash
  sm status
  ```

- **Help**
  Show help message and usage information.
  ```bash
  sm --help
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
- create-domain assumes that SageMaker provisioning and execution roles exist in the governance account.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
