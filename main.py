import flet as ft
import json
import os

# Persistence File
DATA_FILE = "contacts_data.json"

def main(page: ft.Page):
    page.title = "Reach-Out Loop"
    page.theme_mode = ft.ThemeMode.LIGHT
    # page.window_width = 400
    # page.window_height = 700
    page.scroll = ft.ScrollMode.ADAPTIVE

    # State variables
    state = {
        "contacts": [],
        "current_index": 0,
        "is_active": False
    }

    def load_state():
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r") as f:
                data = json.load(f)
                state["contacts"] = data.get("contacts", [])
                state["current_index"] = data.get("current_index", 0)
                state["is_active"] = data.get("is_active", False)

    def save_state():
        with open(DATA_FILE, "w") as f:
            json.dump(state, f)

    load_state()
    print(f"State loaded: {len(state['contacts'])} contacts, index {state['current_index']}, active: {state['is_active']}")

    # --- UI COMPONENTS ---

    # 1. Input View (Paste area)
    bulk_input = ft.TextField(
        label="Paste your full contact list here",
        multiline=True,
        min_lines=10,
        max_lines=15,
        hint_text="One name per line...",
    )

    def process_bulk_input(e):
        lines = bulk_input.value.strip().split("\n")
        raw_names = [line.strip() for line in lines if line.strip()]
        if not raw_names:
            return
        show_filtering_view(raw_names)

    # 2. Filtering View (Check-off list)
    def show_filtering_view(raw_names):
        page.clean()
        checkboxes = []
        
        for name in raw_names:
            # Default to checked if they were previously in the active list
            is_checked = name in state["contacts"] if state["contacts"] else True
            checkboxes.append(ft.Checkbox(label=name, value=is_checked))

        def confirm_selection(e):
            state["contacts"] = [cb.label for cb in checkboxes if cb.value]
            if not state["contacts"]:
                return
            state["current_index"] = 0
            state["is_active"] = True
            save_state()
            show_loop_view()

        page.add(
            ft.Column([
                ft.Text("Select Contacts", size=30, weight=ft.FontWeight.BOLD),
                ft.Text("Check the people you want to keep in this loop:"),
                ft.Column(checkboxes, scroll=ft.ScrollMode.ALWAYS, height=400),
                ft.ElevatedButton(
                    "Start Loop with Selected",
                    on_click=confirm_selection,
                    width=400,
                    bgcolor=ft.Colors.BLUE_600,
                    color=ft.Colors.WHITE
                ),
                ft.TextButton("Go Back", on_click=lambda _: show_selection_view())
            ], spacing=20)
        )
        page.update()

    def show_selection_view():
        page.clean()
        # If we have existing contacts, pre-fill the bulk area
        if state["contacts"]:
             bulk_input.value = "\n".join(state["contacts"])
        
        page.add(
            ft.Column([
                ft.Text("Reach-Out Setup", size=30, weight=ft.FontWeight.BOLD),
                ft.Text("Paste your names below. In the next step, you'll pick who to keep."),
                bulk_input,
                ft.ElevatedButton(
                    "Next: Select from List",
                    on_click=process_bulk_input,
                    width=400,
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
                    color=ft.Colors.WHITE,
                    bgcolor=ft.Colors.BLUE_600
                )
            ], spacing=20, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        )
        page.update()

    # 3. Loop View Components
    contact_display = ft.Text("", size=40, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER)
    progress_display = ft.Text("", size=16, color=ft.Colors.GREY_700)

    def next_contact(e):
        state["current_index"] += 1
        if state["current_index"] >= len(state["contacts"]):
            show_finish_view()
        else:
            update_loop_ui()
            save_state()

    def update_loop_ui():
        if state["contacts"]:
            contact_display.value = state["contacts"][state["current_index"]]
            progress_display.value = f"Contact {state['current_index'] + 1} of {len(state['contacts'])}"
            page.update()

    def reset_loop(e):
        state["is_active"] = False
        save_state()
        show_selection_view()

    def show_loop_view():
        page.clean()
        update_loop_ui()
        page.add(
            ft.Container(
                content=ft.Column([
                    progress_display,
                    ft.Divider(height=40, color=ft.Colors.TRANSPARENT),
                    ft.Container(
                        content=contact_display,
                        padding=40,
                        alignment=ft.alignment.center,
                        border_radius=20,
                        bgcolor=ft.Colors.BLUE_50,
                    ),
                    ft.Divider(height=60, color=ft.Colors.TRANSPARENT),
                    ft.ElevatedButton(
                        "Next Contact",
                        on_click=next_contact,
                        width=400,
                        height=60,
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
                        color=ft.Colors.WHITE,
                        bgcolor=ft.Colors.BLUE_600
                    ),
                    ft.TextButton("Edit List / Reset", on_click=reset_loop)
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=20,
                alignment=ft.alignment.top_center
            )
        )
        page.update()

    def show_finish_view():
        page.clean()
        page.add(
            ft.Column([
                ft.Icon(name=ft.Icons.CHECK_CIRCLE, color=ft.Colors.GREEN, size=100),
                ft.Text("Loop Complete!", size=30, weight=ft.FontWeight.BOLD),
                ft.Text("You've reached out to everyone on your list."),
                ft.Divider(height=40, color=ft.Colors.TRANSPARENT),
                ft.ElevatedButton(
                    "Start Over (Same List)",
                    on_click=lambda _: start_loop_from_beginning(),
                    width=400,
                    bgcolor=ft.Colors.BLUE_600,
                    color=ft.Colors.WHITE
                ),
                ft.TextButton("Edit List / Add People", on_click=reset_loop)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10)
        )
        page.update()

    def start_loop_from_beginning():
        state["current_index"] = 0
        state["is_active"] = True
        save_state()
        show_loop_view()

    # Initial Route
    if state["is_active"] and state["contacts"]:
        print("Routing to Loop View")
        show_loop_view()
    else:
        print("Routing to Selection View")
        show_selection_view()

ft.app(target=main)
