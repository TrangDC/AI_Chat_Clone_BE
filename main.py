import tkinter as tk
from tkinter import scrolledtext, messagebox, simpledialog, Listbox
import json
from app import database
from services.services import *
from datetime import datetime # Import datetime
from app import models, database
import google.generativeai as genai
import os

# --- Initialize Gemini API with API key from environment variable ---
genai.configure(api_key="AIzaSyAUh7P-Zx7TegzSQ31CkpTEWDZzf9_7kcY")
model = genai.GenerativeModel('gemini-2.0-flash-thinking-exp-01-21') # Choose model (gemini-pro is recommended for text)

# --- Prepare Chat session ---
chat = model.start_chat(history=[])

class ChatToolGUI:
    def __init__(self, root):
        self.root = root
        root.title("AI Chat Tool - Test GUI (No JSON Output)")

        self.db = database.SessionLocal() # Khởi tạo session database

        # --- Generate JSON file on startup ---
        write_sessions_to_json_file(self.db) # Call the function to write JSON file

        # --- Các button chức năng ---
        self.btn_show_sessions = tk.Button(root, text="Show All Sessions", command=self.show_all_sessions)
        self.btn_show_sessions.pack(pady=5)

        self.btn_show_session_messages = tk.Button(root, text="Show Session Messages", command=self.show_session_messages)
        self.btn_show_session_messages.pack(pady=5)

        self.btn_create_session = tk.Button(root, text="Create Session", command=self.create_new_session)
        self.btn_create_session.pack(pady=5)

        self.btn_delete_session = tk.Button(root, text="Delete Session", command=self.delete_a_session)
        self.btn_delete_session.pack(pady=5)

        self.btn_show_selected_ai = tk.Button(root, text="Show Selected AI Responses", command=self.show_selected_ai_responses)
        self.btn_show_selected_ai.pack(pady=5)

        self.btn_select_ai_response = tk.Button(root, text="Select AI Response", command=self.select_ai_response_func)
        self.btn_select_ai_response.pack(pady=5)

        self.btn_unselect_ai_response = tk.Button(root, text="Unselect AI Response", command=self.unselect_ai_response_func)
        self.btn_unselect_ai_response.pack(pady=5)

        self.btn_call_gemini_api = tk.Button(root, text="Call Gemini API (Simulated)", command=self.call_gemini_api) # New button
        self.btn_call_gemini_api.pack(pady=5)

        # --- Output Text Area ---
        self.output_text = scrolledtext.ScrolledText(root, height=20, width=80)
        self.output_text.pack(pady=10)

    def display_text_output(self, data):
        """Hiển thị dữ liệu dạng text trong text area."""
        self.output_text.delete(1.0, tk.END) # Xóa nội dung cũ
        if isinstance(data, list): # Xử lý danh sách
            for item in data:
                self.output_text.insert(tk.END, str(item) + "\n---\n") # Hiển thị object representation + separator
        else:
            self.output_text.insert(tk.END, str(data)) # Hiển thị object representation

    def show_all_sessions(self):
        """Hiển thị danh sách sessions."""
        sessions = get_all_sessions(self.db)
        self.display_text_output(sessions) # Hiển thị list sessions object

    def show_session_messages(self):
        """Hiển thị messages của một session cụ thể."""
        session_id = simpledialog.askstring("Input", "Enter Session ID:")
        if session_id:
            messages = get_messages_by_session_id(self.db, session_id)
            self.display_text_output(messages) # Hiển thị list messages object

    def create_new_session(self):
        """Tạo session mới và hiển thị kết quả."""
        session_name = simpledialog.askstring("Input", "Enter Session Name:")
        ai_model = simpledialog.askstring("Input", "Enter AI Model:")
        ai_max_tokens = simpledialog.askinteger("Input", "Enter Max Tokens:", initialvalue=1000)
        ai_response_time = simpledialog.askstring("Input", "Enter Response Time:")

        if session_name and ai_model and ai_max_tokens and ai_response_time:
            new_session = create_session(self.db, session_name, ai_model, ai_max_tokens, ai_response_time)
            self.display_text_output(new_session) # Hiển thị session object
        else:
            messagebox.showwarning("Warning", "Please fill in all session details.")

    def delete_a_session(self):
        """Xóa session và hiển thị kết quả."""
        session_id = simpledialog.askstring("Input", "Enter Session ID to Delete:")
        if session_id:
            if delete_session(self.db, session_id):
                messagebox.showinfo("Success", f"Session '{session_id}' deleted successfully.")
                self.output_text.delete(1.0, tk.END) # Clear output area
            else:
                messagebox.showerror("Error", f"Could not delete session '{session_id}' or session not found.")

    def show_selected_ai_responses(self):
        """Hiển thị danh sách AI responses đã chọn."""
        selected_responses = get_ai_selected_questions(self.db)
        self.display_text_output(selected_responses) # Hiển thị list messages object

    def get_message_id_from_dialog(self, prompt):
        """Hàm helper để lấy message_id từ dialog."""
        message_id = simpledialog.askstring("Input", prompt)
        if not message_id:
            messagebox.showwarning("Warning", "Message ID cannot be empty.")
            return None
        return message_id

    def select_ai_response_func(self):
        """Chọn AI response và hiển thị kết quả."""
        message_id = self.get_message_id_from_dialog("Enter Message ID of AI Response to Select:")
        if message_id:
            selected_response = select_ai_response(self.db, message_id)
            if selected_response:
                self.display_text_output(selected_response) # Hiển thị message object
            else:
                messagebox.showerror("Error", "Could not select AI response or message not found/not AI.")

    def unselect_ai_response_func(self):
        """Bỏ chọn AI response và hiển thị kết quả."""
        message_id = self.get_message_id_from_dialog("Enter Message ID of AI Response to Unselect:")
        if message_id:
            unselected_response = unselect_ai_response(self.db, message_id)
            if unselected_response:
                self.display_text_output(unselected_response) # Hiển thị message object
            else:
                messagebox.showerror("Error", "Could not unselect AI response or message not found/not AI.")

    def call_gemini_api(self): # Renamed from call_gemini_api_simulated to call_gemini_api
        """Calls the real Gemini API and creates a message."""
        session_id = simpledialog.askstring("Input", "Enter Session ID to add AI message:")
        user_prompt = simpledialog.askstring("Input", "Enter User Prompt:")
        if session_id and user_prompt:
            try:
                
                # --- Construct Conversation History (for context) ---
                # history = self.get_prompt_history_for_gemini_api(session_id)

                # --- Send user prompt to Gemini API ---
                response = chat.send_message(user_prompt)
                ai_response_content = response.text

                # --- Create message AI in database ---
                new_ai_message = self.create_ai_message(session_id, ai_response_content)
                if new_ai_message:
                    self.display_text_output(new_ai_message)
                else:
                    messagebox.showerror("Error", "Failed to create AI message in database.")

            except Exception as e:
                messagebox.showerror("Error", f"Error calling Gemini API: {e}")
        else:
            messagebox.showwarning("Warning", "Please enter Session ID and User Prompt.")

    def get_prompt_history_for_gemini_api(self, session_id):
        """Retrieves and formats conversation history for Gemini API."""
        db = self.db
        latest_summary = db.query(models.Summary).filter(
            models.Summary.session_id == session_id
        ).order_by(models.Summary.to_statement_index.desc()).first()

        history = []
        last_statement_index_summarized = 0

        if latest_summary:
            history.append(genai.types.ContentDict(role="model", parts=[latest_summary.summary_text])) # Gemini role: model
            last_statement_index_summarized = latest_summary.to_statement_index

        new_messages = db.query(models.Message).filter(
            models.Message.session_id == session_id,
            models.Message.statement_index > last_statement_index_summarized
        ).order_by(models.Message.statement_index).all()

        for message in new_messages:
            gemini_role = "user" if message.sender == "user" else "model" # Map sender to Gemini roles
            history.append(genai.types.ContentDict(role=gemini_role, parts=[message.content]))

        return history


    def create_ai_message(self, session_id, content):
        """Creates message AI in database (reused, no changes needed in core logic)."""
        db_session = self.db.query(models.Session).filter(models.Session.session_id == session_id).first()
        if not db_session:
            messagebox.showerror("Error", f"Session with ID '{session_id}' not found.")
            return None

        next_statement_index = 1 # Default index if no messages yet
        last_message = db_session.messages
        if last_message:
            last_statement_index_msg = sorted(db_session.messages, key=lambda msg: msg.statement_index)[-1]
            next_statement_index = last_statement_index_msg.statement_index + 1 if last_statement_index_msg else 1


        new_message = models.Message(
            message_id=f"msg_ai_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}",
            session_id=session_id,
            statement_index=next_statement_index,
            sender='system',
            content=content,
            timestamp=datetime.now()
        )
        self.db.add(new_message)
        self.db.commit()
        self.db.refresh(new_message)
        return new_message


    def __del__(self):
        """Đóng database session khi GUI đóng."""
        if hasattr(self, 'db') and self.db:
            self.db.close()

if __name__ == "__main__":
    root = tk.Tk()
    gui = ChatToolGUI(root)
    root.mainloop()