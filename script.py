
"""
═══════════════════════════════════════════════════════════════════
    APLICAȚIE DESKTOP - DETECȚIE EMOȚII DIN FOTOGRAFII
    Autor: [Numele Tău]
    Anul: 2026
    Tehnologii: Python, DeepFace, Tkinter, OpenCV
═══════════════════════════════════════════════════════════════════
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk, ImageDraw
import cv2
from deepface import DeepFace
import os
import threading


class EmotionDetectorApp:
    """Aplicație principală pentru detecția emoțiilor"""

    def __init__(self, root):
        self.root = root
        self.root.title("🎭 Detecție Emoții - Aplicație Desktop")
        self.root.geometry("1000x750")
        self.root.configure(bg='#f5f5f5')
        self.root.resizable(False, False)

        # Variabile
        self.image_path = None
        self.original_image = None
        self.processing = False

        # Creare UI
        self.create_widgets()

        # Centreaza fereastra pe ecran
        self.center_window()

    def center_window(self):
        """Centrează fereastra pe ecran"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def create_widgets(self):
        """Creează interfața grafică"""

        # ═══════════════════════════════════════════════════════
        # HEADER
        # ═══════════════════════════════════════════════════════
        header_frame = tk.Frame(self.root, bg='#4CAF50', height=100)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)

        title = tk.Label(
            header_frame,
            text="🎭 DETECȚIE EMOȚII DIN FOTOGRAFII",
            font=('Arial', 26, 'bold'),
            bg='#4CAF50',
            fg='white'
        )
        title.pack(pady=25)

        subtitle = tk.Label(
            header_frame,
            text="Tehnologie: Deep Learning | Model: DeepFace VGG",
            font=('Arial', 11),
            bg='#4CAF50',
            fg='#E8F5E9'
        )
        subtitle.pack()

        # ═══════════════════════════════════════════════════════
        # TOOLBAR - Butoane
        # ═══════════════════════════════════════════════════════
        toolbar_frame = tk.Frame(self.root, bg='#f5f5f5', height=80)
        toolbar_frame.pack(fill='x', pady=15)

        button_container = tk.Frame(toolbar_frame, bg='#f5f5f5')
        button_container.pack()

        # Buton Încarcă
        self.load_btn = tk.Button(
            button_container,
            text="📂 Încarcă Fotografie",
            command=self.load_image,
            font=('Arial', 13, 'bold'),
            bg='#2196F3',
            fg='white',
            activebackground='#1976D2',
            activeforeground='white',
            padx=25,
            pady=12,
            cursor='hand2',
            relief='flat',
            borderwidth=0
        )
        self.load_btn.pack(side='left', padx=8)

        # Buton Detectează
        self.detect_btn = tk.Button(
            button_container,
            text="🔍 Detectează Emoția",
            command=self.detect_emotion_threaded,
            font=('Arial', 13, 'bold'),
            bg='#FF9800',
            fg='white',
            activebackground='#F57C00',
            activeforeground='white',
            padx=25,
            pady=12,
            cursor='hand2',
            state='disabled',
            relief='flat',
            borderwidth=0
        )
        self.detect_btn.pack(side='left', padx=8)

        # Buton Șterge
        self.clear_btn = tk.Button(
            button_container,
            text="🗑️ Șterge Tot",
            command=self.clear_all,
            font=('Arial', 13, 'bold'),
            bg='#f44336',
            fg='white',
            activebackground='#D32F2F',
            activeforeground='white',
            padx=25,
            pady=12,
            cursor='hand2',
            relief='flat',
            borderwidth=0
        )
        self.clear_btn.pack(side='left', padx=8)

        # Buton Salvează Rezultat
        self.save_btn = tk.Button(
            button_container,
            text="💾 Salvează Rezultat",
            command=self.save_result,
            font=('Arial', 13, 'bold'),
            bg='#9C27B0',
            fg='white',
            activebackground='#7B1FA2',
            activeforeground='white',
            padx=25,
            pady=12,
            cursor='hand2',
            state='disabled',
            relief='flat',
            borderwidth=0
        )
        self.save_btn.pack(side='left', padx=8)

        # ═══════════════════════════════════════════════════════
        # MAIN CONTENT - Imagine și Rezultate
        # ═══════════════════════════════════════════════════════
        main_frame = tk.Frame(self.root, bg='#f5f5f5')
        main_frame.pack(pady=10, padx=25, fill='both', expand=True)

        # ═══════════════════════════════════════════════════════
        # STÂNGA - Imagine
        # ═══════════════════════════════════════════════════════
        image_frame = tk.LabelFrame(
            main_frame,
            text="  📷 Fotografie Încărcată  ",
            font=('Arial', 13, 'bold'),
            bg='white',
            fg='#333',
            relief='solid',
            borderwidth=1
        )
        image_frame.pack(side='left', padx=10, fill='both', expand=True)

        self.image_label = tk.Label(
            image_frame,
            text="📁\n\nNicio imagine încărcată\n\n"
                 "Apasă butonul 'Încarcă Fotografie'\n"
                 "pentru a selecta o imagine",
            font=('Arial', 12),
            bg='white',
            fg='#999',
            justify='center'
        )
        self.image_label.pack(pady=30, padx=20, expand=True)

        # ═══════════════════════════════════════════════════════
        # DREAPTA - Rezultate
        # ═══════════════════════════════════════════════════════
        result_frame = tk.LabelFrame(
            main_frame,
            text="  🎯 Rezultate Detecție  ",
            font=('Arial', 13, 'bold'),
            bg='white',
            fg='#333',
            relief='solid',
            borderwidth=1
        )
        result_frame.pack(side='right', padx=10, fill='both', expand=True)

        # Container rezultate
        result_container = tk.Frame(result_frame, bg='white')
        result_container.pack(fill='both', expand=True, pady=15)

        # Emoție detectată
        emotion_container = tk.Frame(result_container, bg='#E3F2FD', relief='solid', borderwidth=1)
        emotion_container.pack(pady=15, padx=20, fill='x')

        tk.Label(
            emotion_container,
            text="Emoție Detectată:",
            font=('Arial', 11),
            bg='#E3F2FD',
            fg='#666'
        ).pack(pady=(10, 5))

        self.emotion_label = tk.Label(
            emotion_container,
            text="-",
            font=('Arial', 24, 'bold'),
            bg='#E3F2FD',
            fg='#1565C0'
        )
        self.emotion_label.pack(pady=5)

        # Emoji mare
        self.emoji_label = tk.Label(
            emotion_container,
            text="",
            font=('Arial', 70),
            bg='#E3F2FD'
        )
        self.emoji_label.pack(pady=10)

        # Încredere
        self.confidence_label = tk.Label(
            emotion_container,
            text="Încredere: -",
            font=('Arial', 13, 'bold'),
            bg='#E3F2FD',
            fg='#388E3C'
        )
        self.confidence_label.pack(pady=(5, 15))

        # Separator
        separator = tk.Frame(result_container, height=2, bg='#E0E0E0')
        separator.pack(fill='x', padx=20, pady=10)

        # Tabel probabilități
        prob_title = tk.Label(
            result_container,
            text="📊 Distribuție Probabilități:",
            font=('Arial', 12, 'bold'),
            bg='white',
            fg='#333'
        )
        prob_title.pack(pady=(10, 5))

        self.prob_frame = tk.Frame(result_container, bg='white')
        self.prob_frame.pack(pady=10, padx=25, fill='both', expand=True)

        # ═══════════════════════════════════════════════════════
        # FOOTER - Status Bar
        # ═══════════════════════════════════════════════════════
        footer_frame = tk.Frame(self.root, bg='#E0E0E0', height=35)
        footer_frame.pack(fill='x', side='bottom')
        footer_frame.pack_propagate(False)

        self.status_label = tk.Label(
            footer_frame,
            text="📌 Status: Gata | Așteptând fotografie...",
            font=('Arial', 10),
            bg='#E0E0E0',
            fg='#555',
            anchor='w'
        )
        self.status_label.pack(side='left', padx=15, pady=8)

        copyright_label = tk.Label(
            footer_frame,
            text="© 2026 - Aplicație Detecție Emoții | Python + DeepFace",
            font=('Arial', 9),
            bg='#E0E0E0',
            fg='#888'
        )
        copyright_label.pack(side='right', padx=15)

    def load_image(self):
        """Încarcă fotografia din fișier"""
        file_path = filedialog.askopenfilename(
            title="Selectează o fotografie cu o față",
            filetypes=[
                ("Imagini", "*.jpg *.jpeg *.png *.bmp *.gif"),
                ("JPEG", "*.jpg *.jpeg"),
                ("PNG", "*.png"),
                ("Toate fișierele", "*.*")
            ]
        )

        if file_path:
            try:
                self.image_path = file_path

                # Încarcă imaginea
                image = Image.open(file_path)
                self.original_image = image.copy()

                # Redimensionează pentru afișare (păstrează aspect ratio)
                display_image = self.resize_image(image, max_width=420, max_height=420)
                photo = ImageTk.PhotoImage(display_image)

                # Afișează imaginea
                self.image_label.configure(image=photo, text="")
                self.image_label.image = photo

                # Activează butoanele
                self.detect_btn.config(state='normal')

                # Resetează rezultatele
                self.reset_results()

                # Update status
                filename = os.path.basename(file_path)
                self.status_label.config(
                    text=f"📌 Status: Fotografie încărcată - {filename}"
                )

            except Exception as e:
                messagebox.showerror(
                    "Eroare",
                    f"Nu s-a putut încărca imaginea!\n\n{str(e)}"
                )

    def resize_image(self, image, max_width=400, max_height=400):
        """Redimensionează imaginea păstrând aspect ratio"""
        width, height = image.size

        # Calculează noul size
        ratio = min(max_width / width, max_height / height)
        new_width = int(width * ratio)
        new_height = int(height * ratio)

        return image.resize((new_width, new_height), Image.Resampling.LANCZOS)

    def detect_emotion_threaded(self):
        """Detectează emoția în thread separat (nu blochează UI)"""
        if self.processing:
            return

        if not self.image_path:
            messagebox.showerror("Eroare", "Te rog încarcă o fotografie mai întâi!")
            return

        # Pornește thread
        thread = threading.Thread(target=self.detect_emotion)
        thread.daemon = True
        thread.start()

    def detect_emotion(self):
        """Detectează emoția din fotografie folosind DeepFace"""
        self.processing = True

        try:
            # Update UI
            self.status_label.config(text="⏳ Status: Procesare... Detectare emoție în curs...")
            self.detect_btn.config(state='disabled', text="⏳ Procesare...")
            self.emotion_label.config(text="Se procesează...")
            self.root.update()

            # ═══════════════════════════════════════════════════
            # DETECTARE CU DEEPFACE
            # ═══════════════════════════════════════════════════
            result = DeepFace.analyze(
                img_path=self.image_path,
                actions=['emotion'],
                enforce_detection=False,  # Continuă chiar dacă nu detectează față perfect
                detector_backend='opencv'  # Folosește OpenCV (mai rapid)
            )

            # Extrage rezultatul
            if isinstance(result, list):
                result = result[0]

            # Emoția dominantă și probabilități
            emotion = result['dominant_emotion']
            emotions_prob = result['emotion']

            # ═══════════════════════════════════════════════════
            # MAPARE EMOȚII
            # ═══════════════════════════════════════════════════
            emotion_emoji = {
                'angry': '😠',
                'disgust': '🤢',
                'fear': '😨',
                'happy': '😊',
                'sad': '😢',
                'surprise': '😲',
                'neutral': '😐'
            }

            emotion_ro = {
                'angry': 'Furie',
                'disgust': 'Dezgust',
                'fear': 'Frică',
                'happy': 'Bucurie',
                'sad': 'Tristețe',
                'surprise': 'Surpriză',
                'neutral': 'Neutru'
            }

            emotion_color = {
                'angry': '#f44336',
                'disgust': '#9C27B0',
                'fear': '#FF9800',
                'happy': '#4CAF50',
                'sad': '#2196F3',
                'surprise': '#FFEB3B',
                'neutral': '#9E9E9E'
            }

            # ═══════════════════════════════════════════════════
            # AFIȘARE REZULTATE
            # ═══════════════════════════════════════════════════
            emotion_name = emotion_ro.get(emotion, emotion.title())
            emoji = emotion_emoji.get(emotion, '🎭')
            confidence = emotions_prob[emotion]
            color = emotion_color.get(emotion, '#333')

            # Update labels
            self.emotion_label.config(text=emotion_name, fg=color)
            self.emoji_label.config(text=emoji)
            self.confidence_label.config(text=f"Încredere: {confidence:.1f}%")

            # Afișează toate probabilitățile
            self.show_probabilities(emotions_prob, emotion_ro, emotion_color)

            # Activează butonul de salvare
            self.save_btn.config(state='normal')

            # Update status
            self.status_label.config(
                text=f"✅ Status: Detecție completă - {emotion_name} ({confidence:.1f}%)"
            )

            # Success message
            messagebox.showinfo(
                "Detecție Completă",
                f"Emoție detectată: {emotion_name}\n"
                f"Încredere: {confidence:.1f}%\n\n"
                f"Poți vedea toate probabilitățile în panoul din dreapta."
            )

        except Exception as e:
            error_msg = str(e)

            # Mesaje de eroare mai prietenoase
            if "Face could not be detected" in error_msg:
                messagebox.showerror(
                    "Nicio Față Detectată",
                    "Nu s-a putut detecta nicio față în imagine!\n\n"
                    "Asigură-te că:\n"
                    "• Imaginea conține o față clară și vizibilă\n"
                    "• Fața nu este prea mică sau prea mare\n"
                    "• Imaginea are o calitate bună\n"
                    "• Fața este orientată frontal"
                )
            else:
                messagebox.showerror(
                    "Eroare la Procesare",
                    f"A apărut o eroare la detectarea emoției!\n\n"
                    f"Detalii tehnice:\n{error_msg}\n\n"
                    f"Te rog încearcă cu o altă imagine."
                )

            self.emotion_label.config(text="Eroare", fg='#f44336')
            self.status_label.config(text="❌ Status: Eroare la procesare")

        finally:
            self.processing = False
            self.detect_btn.config(state='normal', text="🔍 Detectează Emoția")

    def show_probabilities(self, probabilities, emotion_ro, emotion_color):
        """Afișează probabilitățile tuturor emoțiilor cu bare colorate"""
        # Șterge conținutul vechi
        for widget in self.prob_frame.winfo_children():
            widget.destroy()

        # Sortează după probabilitate (descrescător)
        sorted_emotions = sorted(
            probabilities.items(),
            key=lambda x: x[1],
            reverse=True
        )

        # Afișează fiecare emoție
        for emotion, prob in sorted_emotions:
            # Frame pentru fiecare rând
            row_frame = tk.Frame(self.prob_frame, bg='white')
            row_frame.pack(fill='x', pady=4)

            # Nume emoție
            emotion_name = emotion_ro.get(emotion, emotion.title())
            color = emotion_color.get(emotion, '#333')

            label = tk.Label(
                row_frame,
                text=f"{emotion_name}:",
                font=('Arial', 10, 'bold'),
                bg='white',
                fg=color,
                width=10,
                anchor='w'
            )
            label.pack(side='left', padx=(0, 10))

            # Bară progres colorată
            progress_bg = tk.Canvas(row_frame, width=180, height=22,
                                    bg='#F5F5F5', highlightthickness=0)
            progress_bg.pack(side='left', padx=5)

            # Desenează bara colorată
            bar_width = int((prob / 100) * 180)
            progress_bg.create_rectangle(
                0, 0, bar_width, 22,
                fill=color, outline=''
            )

            # Valoare procentuală
            value = tk.Label(
                row_frame,
                text=f"{prob:.1f}%",
                font=('Arial', 10, 'bold'),
                bg='white',
                fg='#333',
                width=7,
                anchor='e'
            )
            value.pack(side='left', padx=(5, 0))

    def reset_results(self):
        """Resetează rezultatele"""
        self.emotion_label.config(text="-", fg='#1565C0')
        self.emoji_label.config(text="")
        self.confidence_label.config(text="Încredere: -")
        self.save_btn.config(state='disabled')

        # Șterge tabelul probabilități
        for widget in self.prob_frame.winfo_children():
            widget.destroy()

    def clear_all(self):
        """Șterge totul și resetează aplicația"""
        # Confirmare
        if self.image_path:
            confirm = messagebox.askyesno(
                "Confirmare",
                "Sigur vrei să ștergi imaginea și rezultatele?",
                icon='question'
            )
            if not confirm:
                return

        # Reset variabile
        self.image_path = None
        self.original_image = None

        # Reset UI
        self.image_label.configure(
            image='',
            text="📁\n\nNicio imagine încărcată\n\n"
                 "Apasă butonul 'Încarcă Fotografie'\n"
                 "pentru a selecta o imagine"
        )

        self.reset_results()

        # Dezactivează butoane
        self.detect_btn.config(state='disabled')
        self.save_btn.config(state='disabled')

        # Update status
        self.status_label.config(text="📌 Status: Gata | Așteptând fotografie...")

    def save_result(self):
        """Salvează rezultatul într-un fișier text"""
        if not self.image_path:
            return

        try:
            # Cere utilizatorului unde să salveze
            save_path = filedialog.asksaveasfilename(
                title="Salvează rezultatul",
                defaultextension=".txt",
                filetypes=[
                    ("Fișier text", "*.txt"),
                    ("Toate fișierele", "*.*")
                ]
            )

            if save_path:
                # Extrage informațiile
                emotion_text = self.emotion_label.cget("text")
                confidence_text = self.confidence_label.cget("text")

                # Creează conținutul
                content = f"""
═══════════════════════════════════════════════════════════
    RAPORT DETECȚIE EMOȚII
═══════════════════════════════════════════════════════════

Imagine analizată: {os.path.basename(self.image_path)}
Data/Ora: {self.__get_timestamp()}

REZULTAT:
---------
Emoție detectată: {emotion_text}
{confidence_text}

DISTRIBUȚIE PROBABILITĂȚI:
-------------------------
"""
                # Adaugă toate probabilitățile
                for widget in self.prob_frame.winfo_children():
                    labels = [w for w in widget.winfo_children() if isinstance(w, tk.Label)]
                    if len(labels) >= 2:
                        emotion_name = labels[0].cget("text")
                        prob_value = labels[1].cget("text")
                        content += f"{emotion_name:15} {prob_value}\n"

                content += f"""
═══════════════════════════════════════════════════════════
Tehnologie: DeepFace (VGG Model)
Framework: Python + Tkinter
═══════════════════════════════════════════════════════════
"""

                # Salvează
                with open(save_path, 'w', encoding='utf-8') as f:
                    f.write(content)

                messagebox.showinfo(
                    "Salvare Reușită",
                    f"Rezultatul a fost salvat cu succes!\n\n{save_path}"
                )

        except Exception as e:
            messagebox.showerror(
                "Eroare la Salvare",
                f"Nu s-a putut salva rezultatul!\n\n{str(e)}"
            )

    def __get_timestamp(self):
        """Returnează timestamp-ul curent"""
        from datetime import datetime
        return datetime.now().strftime("%d/%m/%Y %H:%M:%S")


def main():
    """Funcția principală - pornește aplicația"""
    root = tk.Tk()
    app = EmotionDetectorApp(root)

    # Icon (opțional - comentează dacă nu ai icon)
    # root.iconbitmap('icon.ico')

    root.mainloop()


if __name__ == "__main__":
    print("═" * 60)
    print("  🎭 APLICAȚIE DETECȚIE EMOȚII DIN FOTOGRAFII")
    print("  Pornire aplicație...")
    print("═" * 60)
    main()