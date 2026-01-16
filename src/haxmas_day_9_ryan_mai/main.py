from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, Button, Label
from textual.containers import Grid, Vertical, Center
from textual.screen import Screen
from datetime import date, timedelta
from google import genai
from google.genai import types
from dotenv import load_dotenv
import os

load_dotenv()

class DayScreen(Screen):
    CSS = """
        DayScreen {
            align: center middle;
        }

        #dialog {
            width: 50;
            height: auto;
            border: thick #1a7431;
            background: $surface;
            padding: 2;
            align: center middle;
        }

        #dialog Label {
            width: 100%;
            text-align: center;
            margin-bottom: 1;
        }

        #dialog Button {
            width: auto;
        }
    """

    def __init__(self, day: int) -> None:
        self.day = day
        super().__init__()

    def compose(self) -> ComposeResult:
        with Vertical(id="dialog"):
            yield Label("Accessing Santa's Naughty List", id="gift-label")
            with Center():
                yield Button("Close", id="close", variant="error")
    
    async def on_mount(self) -> None:
        gift = await self.get_gift()
        self.query_one("#gift-label", Label).update(f"Day {self.day}: {gift}")
        

    async def get_gift(self) -> str:
        try:
            client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
            instruction = "You are Santa, and each day you are offering a gift to a teenager who loves learning to code!"
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                config=types.GenerateContentConfig(
                    system_instruction=instruction,
                    max_output_tokens=1500
                ),
                contents=f"What is the coding gift for day {self.day} of 25 days",
            )
            
            santa_message = response.text.strip() if response.text else "No gifts. Only coal for you naughty pal!"
            return santa_message

        except Exception as e:
            return f"Can't get to Santa: {str(e)}"
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "close":
            self.dismiss()
        event.stop()

class AdventCalendarApp(App):
    
    CSS = """
        Grid {
            grid-size: 5 5;
            grid-gutter: 1 2;
        }

        Grid Button {
            width: 100%;
            height: 100%;
            content-align: center middle;
            text-style: bold;
            color: white;
            background: #333;
            border: none;
        }

        Grid Button:hover {
            background: #1a7431;
        }

        Grid Button.opened {
            background: #2dc653;
        }

        Grid Button.locked {
            background: #ee2e31;
            color: #ffcccc;
        }
    """

    BINDINGS = [("d", "toggle_dark", "Toggle dark mode")]
    START_DATE = date(2025, 12, 1)

    def compose(self) -> ComposeResult:
        yield Header()
        with Grid():
            today = date.today()
            month = today.month
            day = today.day
            if month == 12:
                christmasDay = 26
                for i in range(1, christmasDay):
                    if i <= day:
                        yield Button(str(i), id=f"day-{i}")
                    else:
                        yield Button(str(i), id=f"day-{i}").add_class("locked")
            else:
                yield Footer()
        yield Footer()
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        button = event.button
        day_str = str(button.id).replace("day-", "")
        day_int = int(day_str)
        unlock_day = self.START_DATE + timedelta(days=int(day_int) - 1)
        if date.today() < unlock_day:
            self.notify(f"Day {day_int} will unlock on {unlock_day}!")
            return
        if not button.has_class("opened"):
            button.add_class("opened")
        self.push_screen(DayScreen(int(day_int)))
    
    def action_toggle_dark(self) -> None:
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )

def main():
    app = AdventCalendarApp()
    app.run()
    
if __name__ == "__main__":
    main()