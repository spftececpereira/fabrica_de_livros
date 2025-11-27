from locust import HttpUser, task, between
import random

class BookFactoryUser(HttpUser):
    wait_time = between(1, 5)
    token = None

    def on_start(self):
        """Autentica o usuário ao iniciar"""
        # Gerar usuário único para evitar conflitos
        unique_id = random.randint(10000, 99999)
        self.email = f"loadtest_{unique_id}@example.com"
        self.password = "S3cr3t!Pass"
        
        # Registrar
        self.client.post("/api/v1/auth/register", json={
            "email": self.email,
            "password": self.password,
            "full_name": f"Load Tester {unique_id}"
        })
        
        # Login
        response = self.client.post("/api/v1/auth/login", data={
            "username": self.email,
            "password": self.password
        })
        
        if response.status_code == 200:
            self.token = response.json()["access_token"]
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            print(f"Falha no login para {self.email}")

    @task(3)
    def view_dashboard(self):
        """Simula acesso ao dashboard (endpoints de leitura)"""
        if not self.token: return
        
        self.client.get("/api/v1/users/me", headers=self.headers)
        self.client.get("/api/v1/users/stats/overview", headers=self.headers)
        self.client.get("/api/v1/users/me/activity", headers=self.headers)

    @task(1)
    def create_book_flow(self):
        """Simula fluxo completo de criação de livro"""
        if not self.token: return
        
        # 1. Criar livro (draft)
        book_data = {
            "title": f"Livro de Teste {random.randint(1, 1000)}",
            "description": "Um livro gerado pelo teste de carga",
            "style": random.choice(["cartoon", "realistic", "manga"]),
            "pages_count": 5
        }
        
        response = self.client.post("/api/v1/books/", json=book_data, headers=self.headers)
        
        if response.status_code == 200:
            book_id = response.json()["id"]
            
            # 2. Iniciar geração
            self.client.post(f"/api/v1/books/{book_id}/generate", headers=self.headers)
            
            # 3. Polling de status (simulando WebSocket)
            # Em um teste real, checaríamos até estar completo, mas aqui faremos apenas alguns checks
            for _ in range(3):
                self.client.get(f"/api/v1/books/{book_id}", headers=self.headers)
