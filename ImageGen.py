import tkinter as tk
from PIL import Image, ImageTk
import random
import sqlite3
import os
import hashlib

class ImageGeneratorApp:
    # Constantes da Classe
    IMAGE_WIDTH = 250
    IMAGE_HEIGHT = 200
    UPDATE_INTERVAL = 150
    DATABASE_PATH = os.path.join("Data", "image_database.db")
    GENERATED_FOLDER = "Generated"

    def __init__(self, root):
        try:
            # Inicialização da aplicação
            self.root = root
            self.root.title("Image Generator")
            self.root.geometry("550x350")  # Ajuste do tamanho da janela

            # Criação da pasta de imagens geradas e do banco de dados
            self.create_generated_folder()
            self.create_database()

            # Configuração do canvas para exibir imagens
            self.image_canvas = tk.Canvas(self.root, width=self.IMAGE_WIDTH, height=self.IMAGE_HEIGHT)
            self.image_canvas.pack()

            # Inicialização de variáveis e elementos da interface
            self.generated_image_data = set()

            # Labels da interface
            self.database_status_label = tk.Label(self.root, text="Database Conectada: Não")
            self.database_status_label.pack()

            self.database_size_label = tk.Label(self.root, text="Tamanho da Database: N/A")
            self.database_size_label.pack()

            self.last_hash_label = tk.Label(self.root, text="Último Hash: N/A")
            self.last_hash_label.pack()

            # Botão de pausa
            self.pause_button = tk.Button(self.root, text="Pausar", command=self.toggle_pause)
            self.pause_button.pack()

            # Variável de controle para pausa
            self.paused = False

            # Atualiza as etiquetas da interface após a criação
            self.update_interface_labels()

            # Gera e exibe imagens continuamente
            self.generate_and_display_image_continuously()
            self.start_continuous_generation()

            # Associa o evento de fechamento ao método on_closing
            self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        except Exception as e:
            print(f"Erro na inicialização: {e}")

    def toggle_pause(self):
        # Método chamado quando o botão de pausa é pressionado
        self.paused = not self.paused
        if self.paused:
            self.pause_button.config(text="Retomar")
        else:
            self.pause_button.config(text="Pausar")
            # Retoma a geração de imagens imediatamente
            self.generate_and_display_image_continuously()

    def on_closing(self):
        try:
            # Fecha a conexão com o banco de dados e destrói a janela principal
            if self.connection:
                self.connection.close()
            self.root.destroy()
        except Exception as e:
            print(f"Erro ao fechar a aplicação: {e}")

    def __del__(self):
        try:
            # Garante que a conexão com o banco de dados seja fechada ao deletar o objeto
            if self.connection:
                self.connection.close()
        except Exception as e:
            print(f"Erro ao deletar o objeto: {e}")

    def create_generated_folder(self):
        try:
            if not os.path.exists(self.GENERATED_FOLDER):
                os.makedirs(self.GENERATED_FOLDER)
        except Exception as e:
            print(f"Erro ao criar pasta: {e}")

    def create_database(self):
        try:
            # Conecta ao banco de dados SQLite e cria a tabela se não existir
            self.connection = sqlite3.connect(self.DATABASE_PATH)
            self.cursor = self.connection.cursor()

            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS generated_images (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    hash TEXT UNIQUE
                )
            ''')

            # Carrega hashes existentes na memória
            self.cursor.execute("SELECT hash FROM generated_images")
            rows = self.cursor.fetchall()
            self.generated_image_data = set(hash_value[0] for hash_value in rows)
        except Exception as e:
            print(f"Erro ao criar o banco de dados: {e}")

    def save_to_database(self, image_hash):
        try:
            # Adiciona o hash à lista de hashes e insere no banco de dados
            self.generated_image_data.add(image_hash)
            self.cursor.execute("INSERT INTO generated_images (hash) VALUES (?)", (image_hash,))
            self.connection.commit()

            # Atualiza as etiquetas da interface
            self.update_interface_labels()
        except Exception as e:
            print(f"Erro ao salvar no banco de dados: {e}")

    def start_continuous_generation(self):
        try:
            # Inicia a geração contínua após 500 milissegundos
            self.root.after(500, self.generate_and_display_image_continuously)
        except Exception as e:
            print(f"Erro ao iniciar a geração contínua: {e}")

    def generate_and_display_image_continuously(self):
        try:
            if not self.paused:
                # Gera uma imagem única
                unique_random_image = self.generate_unique_random_image()
                image_hash = self.calculate_image_hash(unique_random_image)

                # Verifica se o hash já está no banco de dados
                if image_hash not in self.generated_image_data:
                    # Salva a imagem com o hash como nome do arquivo
                    image_filename = f"{image_hash}.png"
                    image_path = os.path.join(self.GENERATED_FOLDER, image_filename)
                    unique_random_image.save(image_path)

                    # Salva o hash no banco de dados
                    self.save_to_database(image_hash)

                    # Atualiza a etiqueta do último hash
                    self.last_hash_label.config(text=f"Último Hash: {image_hash}")

                    # Exibe a imagem
                    self.display_image(unique_random_image)

                # Chama novamente o método após um intervalo
                self.root.after(self.UPDATE_INTERVAL, self.generate_and_display_image_continuously)
        except Exception as e:
            print(f"Erro na geração contínua de imagem: {e}")

    def calculate_image_hash(self, pil_image):
        try:
            # Converte a imagem para bytes
            image_bytes = pil_image.tobytes()

            # Usa o sha256 do hashlib para um hash mais confiável
            sha256_hash = hashlib.sha256(image_bytes).hexdigest()

            return sha256_hash
        except Exception as e:
            print(f"Erro ao calcular o hash da imagem: {e}")

    def generate_unique_random_image(self):
        try:
            while True:
                # Gera uma imagem aleatória e calcula o hash
                random_image = self.generate_random_image()
                image_hash = self.calculate_image_hash(random_image)

                # Verifica os valores de hash para garantir a singularidade
                if image_hash not in self.generated_image_data:
                    return random_image
        except Exception as e:
            print(f"Erro ao gerar imagem única: {e}")

    def generate_random_image(self):
        try:
            # Gera uma imagem RGB com pixels de cores aleatórias
            image = Image.new("RGB", (self.IMAGE_WIDTH, self.IMAGE_HEIGHT), color=self.random_color())
            pixel_data = [(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)) for _ in range(self.IMAGE_WIDTH * self.IMAGE_HEIGHT)]
            image.putdata(pixel_data)
            return image
        except Exception as e:
            print(f"Erro ao gerar imagem aleatória: {e}")

    def random_color(self):
        try:
            # Retorna uma cor aleatória
            color_options = [(0, 0, 0), (255, 255, 255),  # Preto e Branco
                             (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))]  # Cor RGB
            return random.choice(color_options)
        except Exception as e:
            print(f"Erro ao escolher cor aleatória: {e}")

    def display_image(self, pil_image):
        try:
            # Exibe a imagem no canvas
            tk_image = ImageTk.PhotoImage(pil_image)
            self.image_canvas.create_image(0, 0, anchor=tk.NW, image=tk_image)
            self.image_canvas.image = tk_image
        except Exception as e:
            print(f"Erro ao exibir imagem: {e}")

    def update_interface_labels(self):
        try:
            # Atualiza a etiqueta de status do banco de dados
            self.database_status_label.config(text=f"Database Conectada: {'Sim' if self.connection else 'Não'}")

            # Atualiza a etiqueta de tamanho do banco de dados
            database_size_bytes = os.path.getsize(self.DATABASE_PATH)
            database_size_label_text = self.format_size(database_size_bytes)
            self.database_size_label.config(text=f"Tamanho da Database: {database_size_label_text}")
        except Exception as e:
            print(f"Erro ao atualizar etiquetas da interface: {e}")

    def format_size(self, size_in_bytes):
        try:
            # Converte bytes para o formato de tamanho apropriado
            for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
                if size_in_bytes < 1024.0:
                    return f"{size_in_bytes:.2f} {unit}"
                size_in_bytes /= 1024.0
        except Exception as e:
            print(f"Erro ao formatar tamanho: {e}")

if __name__ == "__main__":
    try:
        # Inicia a aplicação
        root = tk.Tk()
        app = ImageGeneratorApp(root)
        root.mainloop()
    except Exception as e:
        print(f"Erro na execução da aplicação: {e}")
