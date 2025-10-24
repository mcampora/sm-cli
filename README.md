# SageMaker Unified Studio CLI

A command-line interface (CLI) tool to simplify the creation and management of AWS SageMaker Unified Studio resources.  

Using this tool, I was able to create a domain, invite accounts to this domain (ie. dev, test, prod), activate blueprints in these accounts (ie. tooling, LakeHouse, Workflow), discover the settings coming with these blueprints, create a project profile with custom settings (ex. the GitHub organization), create projects with custom parameters (ex. the associated GitHub repo).
Ultimately the goal of this POC was to illustrate how to manage the lifecycle of a given transformation pipeline (from development to production). 

A GitHub Actions workflow is building a wheel and publishing it to an S3 bucket.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/mcampora/sm-cli.git
   cd sm-cli
   ```

2. Create a virtual environment (recommended):
   ```bash
   python3 -m venv venv
   # On Windows: venv\Scripts\activate
   source venv/bin/activate
   ```

3. Install the build tools
   ```bash
   pip install --upgrade pip
   python3 -m pip install setuptools wheel build   
   ```

4. Install the package in development mode:
   ```bash
   pip install -e .
   ```

5. Build the package
   ```bash
   python3 -m build
   ```

6. Install the package from anywhere
   ```bash
   pip install git+https://github.com/EBSCOIS/sm-cli.git
   ```

## Configuration

1. Create a ./credentials file and update it with your AWS credentials:
   ```bash
   [default]
   aws_access_key_id=...
   aws_secret_access_key=...
   aws_session_token=...
   ```
   You need to at least define the default profile (the governance account).  
   You can define 3 additional profiles to create a data mesh with 4 accounts:
   - dev
   - test
   - prod

## Available Commands

### Domain Management

- **List Domains**
  List all SageMaker domains in the current region.
  ```bash
  sm domains list
  ```

- **Describe Domain**
  Show detailed information about a specific domain.
  ```bash
  sm domains describe --name <domain_name>
  # or by ID
  sm domains describe --id <domain_id>
  ```

- **Create Domain**
  Create a new SageMaker domain using a manifest file.
  ```bash
  sm domains create --manifest <config_file>
  ```

- **Delete Domain**
  Delete an existing SageMaker domain and its resources.
  ```bash
  sm domains delete --name <domain_name> --force
  # or by ID
  sm domains delete --id <domain_id> --force
  ```

### Account Management

- **List Accounts**
  List all accounts in a domain.
  ```bash
  sm accounts list --domain-name <domain_name>
  # or by domain ID
  sm accounts list --domain-id <domain_id>
  ```

- **Invite Account**
  Invite an AWS account to a domain.
  ```bash
  sm accounts invite --domain-name <domain_name> --account <profile_name>
  # with custom template
  sm accounts invite --domain-id <domain_id> --account test --template custom
  ```

- **Uninvite Account**
  Remove an account from a domain.
  ```bash
  sm accounts uninvite --domain-name <domain_name> --account <profile_name>
  # force uninvite without confirmation
  sm accounts uninvite --domain-id <domain_id> --account test --force
  ```

- **List Blueprints**
  List all blueprints in a domain.
  ```bash
  sm accounts list-blueprints --domain-name <domain_name> --account <profile_name>
  ```

- **Describe Blueprint**
  Show details of a specific blueprint.
  ```bash
  sm accounts describe-blueprint --domain-name <domain_name> --account <profile_name> --name <blueprint_name>
  ```

### Project Management

- **List Projects**
  List all projects in a domain.
  ```bash
  sm projects list --domain-name <domain_name>
  # or by domain ID
  sm projects list --domain-id <domain_id>
  ```

- **Get Project Details**
  Get detailed information about a specific project as JSON.
  ```bash
  sm projects describe --domain-name <domain_name> --name <project_name>
  # or by domain ID
  sm projects describe --domain-id <domain_id> --name <project_name>
  ```
  The output is formatted as pretty-printed JSON by default.

- **Create Project**
  Create a new project in a domain.
  ```bash
  sm projects create --domain-name <domain_name> --name <project_name> --account <profile_name>
  # with custom template
  sm projects create --domain-id <domain_id> --name project_name --account dev --template custom.json
  ```

- **Delete Project**
  Delete a project from a domain.
  ```bash
  sm projects delete --domain-name <domain_name> --name <project_name>
  # force delete without confirmation
  sm projects delete --domain-id <domain_id> --name project_name --force
  ```

### Asset Management

- **Grant Access**
  Grant a project access to an S3 location.
  ```bash
  sm assets grant-access --domain-name <domain_name> --location s3://your-bucket/path/ --project-name <project_name>
  ```

- **Publish Asset**
  Publish a data asset in DataZone.
  ```bash
  sm assets publish --domain-name <domain_name> --project-name <project_name> --asset-name <asset_name>
  ```

### Workflow Management

- **Describe Workflow Environment**
  Get workflow environment details for a specific project.
  ```bash
  sm workflows describe --domain-name <domain_name> --name <project_name>
  # or by domain ID
  sm workflows describe --domain-id <domain_id> --name <project_name>
  ```
  The output includes provisioned resources and other workflow environment details in JSON format.

- **List DAGs**
  List all DAGs in a project's workflow environment.
  ```bash
  sm workflows list-dags --domain-name <domain_name> --name <project_name>
  # or by domain ID
  sm workflows list-dags --domain-id <domain_id> --name <project_name>
  ```

### Utility Commands

- **Status**
  Show the current status of the CLI and AWS configuration.
  ```bash
  sm status --account dev
  ```

- **Help**
  Show help message and usage information.
  ```bash
  sm help
  ```

### Getting Help

For detailed help on any command, use the `--help` flag:

```bash
# Show all available commands
sm --help

# Show help for domains commands
sm domains --help

# Show help for a specific command
sm domains create --help
  ```

## Current limitations or required improvements
- delete-project command returns immediately, the project deletion can take up to 5 minutes. You cannot use the uninvite-account or delete-domain commands until the project is deleted.
- delete-project is not cleaning up its associated Glue database.
- create-domain assumes that SageMaker provisioning and execution roles exist in the governance account.
- grant-access command is not implemented yet.
- publish command is not implemented yet.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
