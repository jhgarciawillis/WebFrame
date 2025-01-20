import os
import subprocess

def run_command(command, success_message, error_message):
    try:
        subprocess.run(command, check=True, shell=True)
        print(f"[SUCCESS] {success_message}")
    except subprocess.CalledProcessError:
        print(f"[ERROR] {error_message}")

def create_file(file_path, content=""):
    with open(file_path, "w") as file:
        file.write(content)
    print(f"[SUCCESS] Created file: {file_path}")

print("[INFO] Creating the main project directory...")
project_dir = "real-estate-website"
os.makedirs(project_dir, exist_ok=True)
os.chdir(project_dir)
print(f"[SUCCESS] Created and navigated to the project directory: {project_dir}")

print("[INFO] Creating the client directory and its subdirectories...")
client_dir = "client"
os.makedirs(client_dir, exist_ok=True)
os.makedirs(os.path.join(client_dir, "public"), exist_ok=True)
os.makedirs(os.path.join(client_dir, "src", "components"), exist_ok=True)
os.makedirs(os.path.join(client_dir, "src", "pages"), exist_ok=True)
os.makedirs(os.path.join(client_dir, "src", "services"), exist_ok=True)
os.makedirs(os.path.join(client_dir, "src", "styles"), exist_ok=True)
print(f"[SUCCESS] Created the client directory and its subdirectories: {client_dir}")

print("[INFO] Creating the server directory and its subdirectories...")
server_dir = "server"
os.makedirs(server_dir, exist_ok=True)
os.makedirs(os.path.join(server_dir, "src", "controllers"), exist_ok=True)
os.makedirs(os.path.join(server_dir, "src", "middlewares"), exist_ok=True)
os.makedirs(os.path.join(server_dir, "src", "models"), exist_ok=True)
os.makedirs(os.path.join(server_dir, "src", "routes"), exist_ok=True)
os.makedirs(os.path.join(server_dir, "src", "services"), exist_ok=True)
print(f"[SUCCESS] Created the server directory and its subdirectories: {server_dir}")

print("[INFO] Creating the ml-service directory and its subdirectories...")
ml_service_dir = "ml-service"
os.makedirs(ml_service_dir, exist_ok=True)
os.makedirs(os.path.join(ml_service_dir, "src", "models"), exist_ok=True)
os.makedirs(os.path.join(ml_service_dir, "src", "preprocessors"), exist_ok=True)
print(f"[SUCCESS] Created the ml-service directory and its subdirectories: {ml_service_dir}")

print("[INFO] Creating empty files...")
create_file(".gitignore")
create_file("README.md")
create_file("docker-compose.yml")
create_file(os.path.join(client_dir, "tailwind.config.js"))
create_file(os.path.join(client_dir, "tsconfig.json"))
create_file(os.path.join(client_dir, "package.json"))
create_file(os.path.join(server_dir, ".env"))
create_file(os.path.join(server_dir, "tsconfig.json"))
create_file(os.path.join(server_dir, "package.json"))
create_file(os.path.join(ml_service_dir, "Dockerfile"))
create_file(os.path.join(ml_service_dir, "src", "app.py"))
create_file(os.path.join(ml_service_dir, "src", "requirements.txt"))

print("[INFO] Creating common pages and components...")
# Client pages
create_file(os.path.join(client_dir, "src", "pages", "Home.tsx"), "// Home page placeholder content")
create_file(os.path.join(client_dir, "src", "pages", "AboutUs.tsx"), "// About Us page placeholder content")
create_file(os.path.join(client_dir, "src", "pages", "Login.tsx"), "// Login page placeholder content")
create_file(os.path.join(client_dir, "src", "pages", "CreateAccount.tsx"), "// Create Account page placeholder content")
create_file(os.path.join(client_dir, "src", "pages", "DeleteAccount.tsx"), "// Delete Account page placeholder content")

# Client components
create_file(os.path.join(client_dir, "src", "components", "Header.tsx"), "// Header component placeholder content")
create_file(os.path.join(client_dir, "src", "components", "Footer.tsx"), "// Footer component placeholder content")
create_file(os.path.join(client_dir, "src", "components", "PropertyCard.tsx"), "// Property Card component placeholder content")
create_file(os.path.join(client_dir, "src", "components", "SearchBar.tsx"), "// Search Bar component placeholder content")

# Server routes
create_file(os.path.join(server_dir, "src", "routes", "authRoutes.ts"), "// Authentication routes placeholder content")
create_file(os.path.join(server_dir, "src", "routes", "propertyRoutes.ts"), "// Property routes placeholder content")

# Server controllers
create_file(os.path.join(server_dir, "src", "controllers", "authController.ts"), "// Authentication controller placeholder content")
create_file(os.path.join(server_dir, "src", "controllers", "propertyController.ts"), "// Property controller placeholder content")

# Server models
create_file(os.path.join(server_dir, "src", "models", "userModel.ts"), "// User model placeholder content")
create_file(os.path.join(server_dir, "src", "models", "propertyModel.ts"), "// Property model placeholder content")

print("[INFO] Initializing a new Node.js project...")
run_command("npm init -y", "Initialized a new Node.js project", "Failed to initialize a new Node.js project")

print("[INFO] Installing backend dependencies...")
run_command("npm install express pg firebase dotenv jsonwebtoken bcrypt", "Installed backend dependencies", "Failed to install backend dependencies")

print("[INFO] Creating a new React app with TypeScript...")
os.chdir(client_dir)
run_command("npx create-react-app . --template typescript --use-npm", "Created a new React app with TypeScript", "Failed to create a new React app with TypeScript")

print("[INFO] Installing additional frontend dependencies...")
run_command("npm install axios react-router-dom firebase", "Installed additional frontend dependencies", "Failed to install additional frontend dependencies")

print("[INFO] Installing Tailwind CSS and its dependencies...")
run_command("npm install -D tailwindcss@latest postcss@latest autoprefixer@latest", "Installed Tailwind CSS and its dependencies", "Failed to install Tailwind CSS and its dependencies")
run_command("npx tailwindcss init -p", "Initialized Tailwind CSS configuration", "Failed to initialize Tailwind CSS configuration")

print("[INFO] Creating a new virtual environment for the ML service...")
os.chdir(os.path.join("..", ml_service_dir))
run_command("python -m venv venv", "Created a new virtual environment for the ML service", "Failed to create a new virtual environment for the ML service")

print("[INFO] Activating the virtual environment and installing dependencies...")
if os.name == "nt":  # For Windows
    run_command(os.path.join("venv", "Scripts", "activate"), "Activated the virtual environment", "Failed to activate the virtual environment")
else:  # For macOS/Linux
    run_command("source " + os.path.join("venv", "bin", "activate"), "Activated the virtual environment", "Failed to activate the virtual environment")
run_command("pip install flask numpy pandas scikit-learn joblib flask-cors", "Installed ML service dependencies", "Failed to install ML service dependencies")

print("[INFO] Initializing a new Git repository...")
os.chdir(os.path.join("..", ".."))
run_command("git init", "Initialized a new Git repository", "Failed to initialize a new Git repository")

print("[SUCCESS] Project structure and configurations completed.")
print("[INFO] Next steps:")
print("1. Implement the backend API in the 'server' directory.")
print("2. Implement the frontend pages and components in the 'client' directory.")
print("3. Implement user authentication and account management using Firebase Authentication.")
print("4. Integrate the ML service by implementing the Flask API and preprocessing scripts.")
print("5. Dockerize the application by creating Dockerfiles and updating the docker-compose.yml file.")
print("6. Test and refine the implemented features.")
print("7. Deploy the application to a hosting platform.")
print("8. Monitor and iterate based on user feedback and requirements.")