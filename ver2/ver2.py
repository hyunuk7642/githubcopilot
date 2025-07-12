import tkinter as tk
from tkinter import messagebox
import openai
import customtkinter as ctk

class JobFinder:
    def __init__(self, root):
        self.root = root
        self.root.title("직업 탐색 프로그램")
        self.root.geometry("1000x800")
        
        # Main container
        self.main_frame = ctk.CTkFrame(root)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # API 키 입력 프레임
        self.api_frame = ctk.CTkFrame(self.main_frame)
        self.api_frame.pack(fill="x", padx=10, pady=5)
        
        self.api_key = tk.StringVar()
        ctk.CTkLabel(self.api_frame, text="OpenAI API Key:").pack(side="left", padx=5)
        self.api_entry = ctk.CTkEntry(self.api_frame, textvariable=self.api_key, width=400)
        self.api_entry.pack(side="left", padx=5)
        
        # Content frame with question area and score display
        self.content_frame = ctk.CTkFrame(self.main_frame)
        self.content_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Left side with questions and slider
        self.left_frame = ctk.CTkFrame(self.content_frame)
        self.left_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        
        # Question area
        self.question_frame = ctk.CTkFrame(self.left_frame)
        self.question_frame.pack(fill="x", padx=10, pady=10)
        
        # Right side score display
        self.score_frame = ctk.CTkFrame(self.content_frame, width=200)
        self.score_frame.pack(side="right", fill="y", padx=5, pady=5)
        self.score_frame.pack_propagate(False)
        
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
        self.question_label = ctk.CTkLabel(
            self.question_frame,
            text=self.questions[0],
            wraplength=600,
            font=("Helvetica", 16),
            anchor="w",
            justify="left"
        )
        self.question_label.pack(fill="x", padx=20, pady=(20,10))

        # 슬라이더 컨테이너
        self.slider_container = ctk.CTkFrame(self.question_frame, fg_color="transparent")
        self.slider_container.pack(fill="x", padx=20, pady=10)

        # 슬라이더 위의 점수 범위 표시
        self.range_frame = ctk.CTkFrame(self.slider_container, fg_color="transparent")
        self.range_frame.pack(fill="x", padx=20)
        ctk.CTkLabel(self.range_frame, text="0", font=("Helvetica", 12)).pack(side="left")
        ctk.CTkLabel(self.range_frame, text="50", font=("Helvetica", 12)).pack(side="right")

        # 슬라이더 생성
        self.score_value = tk.IntVar(value=25)
        self.score_slider = ctk.CTkSlider(
            self.slider_container,
            from_=0,
            to=50,
            number_of_steps=50,
            width=500,
            height=20,
            variable=self.score_value,
            command=self.update_score_display,
            button_color="#2CC985",
            button_hover_color="#2CC985",
            progress_color="#2CC985"
        )
        self.score_slider.pack(pady=5)
        
        # 현재 점수 표시
        self.score_display = ctk.CTkLabel(
            self.slider_container,
            text="25점",
            font=("Helvetica", 14, "bold"),
            text_color="#2CC985"
        )
        self.score_display.pack(pady=5)

        # 다음 버튼
        self.next_button = ctk.CTkButton(
            self.question_frame,
            text="다음",
            width=120,
            height=35,
            command=self.next_question,
            fg_color="#3B8ED0",
            hover_color="#36719F"
        )
        self.next_button.pack(pady=20)
        
        # Initialize score labels
        self.score_labels = []
        for i in range(10):
            score_label = ctk.CTkLabel(
                self.score_frame,
                text=f"질문 {i+1}: -",
                font=("Helvetica", 14)
            )
            score_label.pack(pady=5)
            self.score_labels.append(score_label)
        
        # 결과 텍스트 영역
        self.result_text = ctk.CTkTextbox(
            self.main_frame,
            wrap="word",
            font=("Helvetica", 14),
            height=200
        )
        self.result_text.pack(fill="both", expand=True, padx=10, pady=5)
    
    def update_score_display(self, value=None):
        current_score = int(self.score_value.get())
        self.score_display.configure(text=f"{current_score}점")
        if self.current_question < len(self.score_labels):
            self.score_labels[self.current_question].configure(
                text=f"질문 {self.current_question + 1}: {current_score}점"
            )
    
    def next_question(self):
        if not self.api_key.get():
            messagebox.showerror("오류", "OpenAI API 키를 입력해주세요!")
            return
            
        self.answers.append(self.score_value.get())
        self.current_question += 1
        
        if self.current_question < len(self.questions):
            self.question_label.configure(text=self.questions[self.current_question])
            self.score_value.set(25)  # Reset slider to middle value
        else:
            self.analyze_results()
            self.next_button.configure(state="disabled")
            
    def verify_api_key(self):
        try:
            client = openai.OpenAI(api_key=self.api_key.get())
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
            if not self.verify_api_key():
                return

            client = openai.OpenAI(api_key=self.api_key.get())
            
            # 분석 중임을 표시
            self.result_text.delete("1.0", tk.END)
            self.result_text.insert("1.0", "분석 중입니다... 잠시만 기다려주세요...")
            self.root.update()
            
            # 응답 결과를 문자열로 변환
            response_text = "\n".join([f"Q{i+1}: {q}\nScore: {score}/50" 
                                     for i, (q, score) in enumerate(zip(self.questions, self.answers))])
            
            # GPT에게 보낼 프롬프트 작성
            prompt = f"""
            다음은 직업 적성 검사 결과입니다 (각 질문에 대해 0-50점으로 평가):
            {response_text}
            
            위 응답을 바탕으로 다음과 같이 분석해주세요:

            1단계 - 성향 분석 (1-20단계):
            - 응답자의 특성, 성향, 장단점 등을 점진적으로 더 깊이 분석
            - 각 단계는 이전 단계를 기반으로 더 깊은 통찰 제공
            
            2단계 - 직업 적합도 분석 (21-40단계):
            - 응답자의 성향이 어떤 직무와 잘 맞는지 분석
            - 업무 환경 선호도, 스트레스 대처 방식 등 고려
            
            3단계 - 구체적 추천 (41-50단계):
            - 상위 5개 추천 직업 (구체적으로)
            - 각 직업 추천 이유 (성향과 연계하여 설명)
            - 각 직업별 필요한 준비사항:
              * 필요한 자격증
              * 필요한 교육/학위
              * 필요한 경험/인턴십
              * 구체적인 준비 로드맵
            
            응답 형식:
            단계 1: [분석내용]
            단계 2: [분석내용]
            ...
            단계 50: [분석내용]

            특히 마지막 10단계(41-50단계)에서는 반드시 다음을 포함해주세요:
            - 구체적인 직업명 (모호하지 않게)
            - 해당 직업을 추천하는 명확한 이유
            - 취업을 위한 구체적인 준비사항과 로드맵
            """
            
            # GPT API 호출
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "당신은 진로상담 전문가입니다. 학생들의 적성검사 결과를 매우 상세하게 분석하고 구체적인 직업을 추천해주세요. 추천할 때는 반드시 실제 존재하는 구체적인 직업명을 사용하고, 해당 직업에 필요한 자격요건과 준비과정을 상세히 설명해주세요. 모호한 직업명이나 광범위한 분야명은 사용하지 마세요."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            # 응답 처리 및 표시
            analysis = response.choices[0].message.content
            self.result_text.delete("1.0", tk.END)
            self.result_text.insert("1.0", analysis)
                
        except openai.APIError as e:
            messagebox.showerror("API 오류", f"OpenAI API 오류가 발생했습니다: {str(e)}")
        except Exception as e:
            messagebox.showerror("오류", f"예기치 않은 오류가 발생했습니다: {str(e)}")

if __name__ == "__main__":
    try:
        root = ctk.CTk()
        app = JobFinder(root)
        root.mainloop()
    except Exception as e:
        print(f"프로그램 실행 중 오류가 발생했습니다: {str(e)}")
