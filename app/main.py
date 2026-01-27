from __future__ import annotations

import argparse
from pathlib import Path
from typing import Optional

from agent import KnowledgeBase, LiBaiAgent


def try_recognize_speech(language: str = "zh-CN") -> Optional[str]:
    try:
        import speech_recognition as sr
    except ImportError:
        return None

    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("正在聆听，请开始说话...")
        audio = recognizer.listen(source, phrase_time_limit=10)
    try:
        return recognizer.recognize_google(audio, language=language)
    except sr.UnknownValueError:
        return None
    except sr.RequestError:
        return None


def speak_response(text: str) -> None:
    try:
        import pyttsx3
    except ImportError:
        return

    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()


def main() -> None:
    parser = argparse.ArgumentParser(description="李白智能问答演示")
    parser.add_argument(
        "--data",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "data" / "knowledge.json",
        help="知识库JSON路径",
    )
    parser.add_argument("--voice", action="store_true", help="启用语音识别")
    parser.add_argument("--tts", action="store_true", help="启用语音播报")
    args = parser.parse_args()

    knowledge_base = KnowledgeBase.from_json(args.data)
    agent = LiBaiAgent(knowledge_base)

    if args.voice:
        question = try_recognize_speech() or ""
        if not question:
            print("未识别到语音，请改用键盘输入。")
            question = input("请输入问题：")
    else:
        question = input("请输入问题：")

    answer = agent.answer(question)
    print("\n" + answer)

    if args.tts:
        speak_response(answer)


if __name__ == "__main__":
    main()
