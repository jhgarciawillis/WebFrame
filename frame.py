import os
import sys
import subprocess
import logging
import yaml
import json
import boto3
import firebase_admin
from firebase_admin import credentials
from datetime import datetime
from typing import Dict, Any

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('setup.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ProjectSetup:
    def __init__(self):
        self.project_dir = "real-estate-website"
        self.config = None
        self.aws_client = None
        self.firebase_app = None

    def run_command(self, command: str, success_message: str, error_message: str) -> bool:
        try:
            subprocess.run(command, check=True, shell=True)
            logger.info(success_message)
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"{error_message}: {str(e)}")
            return False

    def create_file(self, file_path: str, content: str = "") -> None:
        try:
            with open(file_path, "w") as file:
                file.write(content)
            logger.info(f"Created file: {file_path}")
        except Exception as e:
            logger.error(f"Failed to create file {file_path}: {str(e)}")

    def create_config_files(self) -> None:
        config_dir = "config"
        os.makedirs(config_dir, exist_ok=True)

        config_template = '''
cloud:
  aws:
    access_key: ""
    secret_key: ""
    region: ""
  firebase:
    project_id: ""
    private_key: ""
    client_email: ""
  database:
    postgres_user: ""
    postgres_password: ""
    host: ""
    port: 5432
    database: "real_estate"

domains:
  primary_domain: ""
  api_domain: ""

ssl:
  email: ""
  provider: "letsencrypt"

monitoring:
  prometheus_port: 9090
  grafana_port: 3000
'''
        self.create_file(os.path.join(config_dir, "credentials_template.yaml"), config_template)

    def load_config(self) -> None:
        config_path = os.path.join("config", "credentials.yaml")
        
        if not os.path.exists(config_path):
            logger.error("credentials.yaml not found. Please copy credentials_template.yaml to credentials.yaml and fill in your credentials.")
            sys.exit(1)
            
        try:
            with open(config_path) as f:
                self.config = yaml.safe_load(f)
            self.validate_config()
        except Exception as e:
            logger.error(f"Failed to load configuration: {str(e)}")
            sys.exit(1)

    def validate_config(self) -> None:
        required_fields = [
            'cloud.aws.access_key',
            'cloud.firebase.project_id',
            'database.postgres_user',
            'domains.primary_domain',
            'ssl.email'
        ]
        
        for field in required_fields:
            if not self.get_nested_dict_value(self.config, field.split('.')):
                raise ValueError(f"Missing required configuration: {field}")

    @staticmethod
    def get_nested_dict_value(dict_obj: Dict, keys: list) -> Any:
        for key in keys:
            if key not in dict_obj:
                return None
            dict_obj = dict_obj[key]
        return dict_obj

    def setup_aws(self) -> None:
        try:
            self.aws_client = boto3.client(
                'ec2',
                aws_access_key_id=self.config['cloud']['aws']['access_key'],
                aws_secret_access_key=self.config['cloud']['aws']['secret_key'],
                region_name=self.config['cloud']['aws']['region']
            )
            logger.info("AWS setup completed successfully")
        except Exception as e:
            logger.error(f"AWS setup failed: {str(e)}")
            raise

    def setup_firebase(self) -> None:
        try:
            firebase_config = {
                "type": "service_account",
                "project_id": self.config['cloud']['firebase']['project_id'],
                "private_key": self.config['cloud']['firebase']['private_key'],
                "client_email": self.config['cloud']['firebase']['client_email']
            }
            
            cred = credentials.Certificate(firebase_config)
            self.firebase_app = firebase_admin.initialize_app(cred)
            
            self.create_file(
                os.path.join(self.project_dir, "client", "src", "config", "firebase.ts"),
                f'export const firebaseConfig = {json.dumps(firebase_config, indent=2)};'
            )
            logger.info("Firebase setup completed successfully")
        except Exception as e:
            logger.error(f"Firebase setup failed: {str(e)}")
            raise

    def setup_database(self) -> None:
        try:
            db_config = self.config['database']
            
            # Create database.env file
            db_env_content = f'''
POSTGRES_USER={db_config['postgres_user']}
POSTGRES_PASSWORD={db_config['postgres_password']}
POSTGRES_DB={db_config['database']}
'''
            self.create_file(os.path.join(self.project_dir, "server", "database.env"), db_env_content)
            
            # Create docker-compose section for database
            db_docker_compose = f'''
  database:
    image: postgres:latest
    env_file:
      - server/database.env
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "{db_config['port']}:5432"
'''
            # Append to docker-compose.yml
            with open(os.path.join(self.project_dir, "docker-compose.yml"), "a") as f:
                f.write(db_docker_compose)
                
            logger.info("Database setup completed successfully")
        except Exception as e:
            logger.error(f"Database setup failed: {str(e)}")
            raise

    def setup_monitoring(self) -> None:
        monitoring_dir = os.path.join(self.project_dir, "monitoring")
        os.makedirs(monitoring_dir, exist_ok=True)
        
        # Prometheus configuration
        prometheus_config = f'''
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'backend'
    static_configs:
      - targets: ['localhost:3000']
  - job_name: 'ml-service'
    static_configs:
      - targets: ['localhost:5000']
'''
        self.create_file(os.path.join(monitoring_dir, "prometheus.yml"), prometheus_config)
        
        # Grafana configuration
        grafana_config = '''
apiVersion: 1
datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
'''
        self.create_file(os.path.join(monitoring_dir, "grafana-datasources.yml"), grafana_config)
        
        # Add to docker-compose
        monitoring_docker_compose = f'''
  prometheus:
    image: prom/prometheus
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "{self.config['monitoring']['prometheus_port']}:9090"

  grafana:
    image: grafana/grafana
    volumes:
      - ./monitoring/grafana-datasources.yml:/etc/grafana/provisioning/datasources/datasources.yml
    ports:
      - "{self.config['monitoring']['grafana_port']}:3000"
    depends_on:
      - prometheus
'''
        with open(os.path.join(self.project_dir, "docker-compose.yml"), "a") as f:
            f.write(monitoring_docker_compose)

    def setup_ssl(self) -> None:
        ssl_config = self.config['ssl']
        
        certbot_command = f'''
certbot certonly \
  --standalone \
  --preferred-challenges http \
  --email {ssl_config['email']} \
  --agree-tos \
  --no-eff-email \
  -d {self.config['domains']['primary_domain']} \
  -d {self.config['domains']['api_domain']}
'''
        self.run_command(certbot_command, "SSL certificates generated successfully", "Failed to generate SSL certificates")

    def setup_ci_cd(self) -> None:
        github_workflow_dir = os.path.join(self.project_dir, ".github", "workflows")
        os.makedirs(github_workflow_dir, exist_ok=True)
        
        ci_cd_config = '''
name: CI/CD Pipeline

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Build and test frontend
        run: |
          cd client
          npm install
          npm run build
          npm test
          
      - name: Build and test backend
        run: |
          cd server
          npm install
          npm run build
          npm test
          
      - name: Build and test ML service
        run: |
          cd ml-service
          pip install -r requirements.txt
          python -m pytest
'''
        self.create_file(os.path.join(github_workflow_dir, "main.yml"), ci_cd_config)

    def setup_project(self) -> None:
        try:
            logger.info("Starting project setup...")
            
            # Create initial config
            self.create_config_files()
            self.load_config()
            
            # Create project directory structure
            os.makedirs(self.project_dir, exist_ok=True)
            os.chdir(self.project_dir)
            
            # Setup cloud services
            self.setup_aws()
            self.setup_firebase()
            self.setup_database()
            
            # Setup monitoring
            self.setup_monitoring()
            
            # Setup SSL
            self.setup_ssl()
            
            # Setup CI/CD
            self.setup_ci_cd()
            
            logger.info("Project setup completed successfully")
            
        except Exception as e:
            logger.error(f"Project setup failed: {str(e)}")
            sys.exit(1)

def main():
    setup = ProjectSetup()
    setup.setup_project()

if __name__ == "__main__":
    main()