import tkinter as tk
from tkinter import ttk, messagebox
import openai

class JobFinder:
    def __init__(self, root):
        self.root = root
        self.root.title("직업 탐색 프로그램")
        self.root.geometry("800x600")
        
        # 스타일 설정
        style = ttk.Style()
        style.configure('TLabelframe', background='white')
        style.configure('TLabel', background='white')
        style.configure('TButton', padding=5)
        
        # API 키 입력 프레임
        self.api_frame = ttk.LabelFrame(root, text="OpenAI API 설정", padding="10")
        self.api_frame.pack(fill="x", padx=10, pady=5)
        
        self.api_key = tk.StringVar()
        ttk.Label(self.api_frame, text="API Key:").pack(side="left")
        self.api_entry = ttk.Entry(self.api_frame, textvariable=self.api_key, width=50)
        self.api_entry.pack(side="left", padx=5)
        
        # 질문 프레임
        self.question_frame = ttk.LabelFrame(root, text="직업 적성 검사", padding="10")
        self.question_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.questions = [
            "1. 새로운 것을 배우는 것을 좋아하시나요?",
            "2. 다른 사람들과 함께 일하는 것을 선호하시나요?",
            "3. 창의적인 활동을 즐기시나요?",
            "4. 규칙적이고 체계적인 일을 선호하시나요?",
            "5. 문제를 해결하는 것을 좋아하시나요?",
            "6. 기술이나 기계를 다루는 것에 관심이 있으신가요?",
            "7. 다른 사람을 돕는 일에 보람을 느끼시나요?",
            "8. 리더십을 발휘하는 것을 좋아하시나요?",
            "9. 세밀한 작업을 잘 하시나요?",
            "10. 새로운 아이디어를 내는 것을 좋아하시나요?"
        ]
        
        self.answers = []
        self.current_question = 0
        
        # 질문 표시 레이블
        self.question_label = ttk.Label(self.question_frame, text=self.questions[0], wraplength=700)
        self.question_label.pack(pady=20)
        
        # 응답 버튼 프레임
        self.button_frame = ttk.Frame(self.question_frame)
        self.button_frame.pack(pady=10)
        
        # 응답 버튼
        self.responses = ["매우 그렇다", "그렇다", "보통이다", "아니다", "매우 아니다"]
        for i, response in enumerate(self.responses):
            ttk.Button(self.button_frame, text=response, command=lambda x=i: self.next_question(x)).pack(side="left", padx=5)
            
        # 결과 텍스트 영역
        self.result_text = tk.Text(root, height=10, wrap="word")
        self.result_text.pack(fill="both", expand=True, padx=10, pady=5)

    def next_question(self, answer):
        if not self.api_key.get():
            messagebox.showerror("오류", "OpenAI API 키를 입력해주세요!")
            return
            
        self.answers.append(self.responses[answer])
        self.current_question += 1
        
        if self.current_question < len(self.questions):
            self.question_label.config(text=self.questions[self.current_question])
        else:
            self.analyze_results()
            
    def verify_api_key(self):
        try:
            client = openai.OpenAI(api_key=self.api_key.get())
            # 간단한 API 테스트
            client.models.list()
            return True
        except Exception as e:
            messagebox.showerror("API 오류", 
                               "API 키가 올바르지 않거나 연결에 문제가 있습니다.\n"
                               "1. API 키가 올바른지 확인해주세요.\n"
                               "2. 인터넷 연결을 확인해주세요.\n"
                               f"오류 메시지: {str(e)}")
            return False

    def analyze_results(self):
        try:
            # API 키 검증
            if not self.verify_api_key():
                return

            client = openai.OpenAI(api_key=self.api_key.get())
            
            # 분석 중임을 표시
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, "분석 중입니다... 잠시만 기다려주세요...")
            self.root.update()
            
            # 응답 결과를 문자열로 변환
            response_text = "\n".join([f"Q{i+1}: {q}\nA: {a}" for i, (q, a) in enumerate(zip(self.questions, self.answers))])
            
            # GPT에게 보낼 프롬프트 작성
            prompt = f"""
            다음은 직업 적성 검사 결과입니다:
            {response_text}
            
            위 응답을 바탕으로:
            1. 응답자의 성향을 분석해주세요
            2. 추천하는 직업 3가지와 그 이유를 설명해주세요
            3. 추천 직업을 위해 준비해야 할 것들을 알려주세요
            """
            
            # GPT API 호출
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "당신은 진로상담 전문가입니다. 학생들의 적성검사 결과를 분석하고 적합한 직업을 추천해주세요."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            # 결과 표시
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, response.choices[0].message.content)
            
            # 버튼 비활성화
            for widget in self.button_frame.winfo_children():
                widget.configure(state="disabled")
                
        except openai.APIError as e:
            messagebox.showerror("API 오류", f"OpenAI API 오류가 발생했습니다: {str(e)}")
        except Exception as e:
            messagebox.showerror("오류", f"예기치 않은 오류가 발생했습니다: {str(e)}")

if __name__ == "__main__":
    try:
        root = tk.Tk()
        root.configure(bg='white')  # 배경색 설정
        
        # macOS에서의 GUI 최적화
        if root.tk.call('tk', 'windowingsystem') == 'aqua':
            root.tk.call('tk::unsupported::MacWindowStyle', 'style', root._w, 'moveableModal', 'closeBox')
        
        app = JobFinder(root)
        root.mainloop()
    except Exception as e:
        print(f"프로그램 실행 중 오류가 발생했습니다: {str(e)}")
