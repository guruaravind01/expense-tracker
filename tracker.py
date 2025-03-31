import curses
import datetime

EXPENSES_FILE = "expenses.txt"


# Load expenses from file
def load_expenses():
    try:
        with open(EXPENSES_FILE, "r") as file:
            expenses = [line.strip().split(", ") for line in file.readlines()]
            return sorted(
                expenses, key=lambda x: datetime.datetime.strptime(x[0], "%d-%m-%Y")
            )
    except FileNotFoundError:
        return []


# Save expenses to file
def save_expenses(expenses):
    with open(EXPENSES_FILE, "w") as file:
        for expense in expenses:
            file.write(", ".join(expense) + "\n")


# Get user input
def get_input(stdscr, y, x, prompt, max_len=20):
    stdscr.addstr(y, x, prompt, curses.color_pair(3) | curses.A_BOLD)
    stdscr.refresh()
    curses.echo()
    user_input = stdscr.getstr(y, x + len(prompt), max_len).decode().strip()
    curses.noecho()
    return user_input


# Validate date format
def get_valid_date(stdscr, y, x, date_label):
    while True:
        date_str = get_input(stdscr, y, x, date_label)
        try:
            datetime.datetime.strptime(date_str, "%d-%m-%Y")
            return date_str
        except ValueError:
            stdscr.addstr(
                y + 1, x, "✖ Invalid date! Use DD-MM-YYYY.", curses.color_pair(1)
            )
            stdscr.refresh()
            stdscr.getch()
            stdscr.addstr(y + 1, x, " " * 40)  # Clear error message


# Validate amount input
def get_valid_amount(stdscr, y, x, amount_label):
    while True:
        amount_str = get_input(stdscr, y, x, amount_label)
        if amount_str.isdigit():
            return amount_str
        stdscr.addstr(y + 1, x, "✖ Enter a valid number.", curses.color_pair(1))
        stdscr.refresh()
        stdscr.getch()
        stdscr.addstr(y + 1, x, " " * 40)


# Draw a border around the content, ensuring it fits within terminal bounds
def draw_border(stdscr, start_y, start_x, height, width):
    max_height, max_width = stdscr.getmaxyx()
    height = min(height, max_height - start_y)
    width = min(width, max_width - start_x)
    if height < 3 or width < 3:
        return

    stdscr.addstr(start_y, start_x, "┌" + "─" * (width - 2) + "┐", curses.color_pair(5))
    for i in range(1, height - 1):
        stdscr.addstr(start_y + i, start_x, "│", curses.color_pair(5))
        stdscr.addstr(start_y + i, start_x + width - 1, "│", curses.color_pair(5))
    stdscr.addstr(
        start_y + height - 1,
        start_x,
        "└" + "─" * (width - 2) + "┘",
        curses.color_pair(5),
    )


# Main menu
def main(stdscr):
    curses.start_color()
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)  # Errors
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)  # Success
    curses.init_pair(3, curses.COLOR_CYAN, curses.COLOR_BLACK)  # Input prompts
    curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_BLACK)  # Menu items
    curses.init_pair(5, curses.COLOR_MAGENTA, curses.COLOR_BLACK)  # Borders and headers

    expenses = load_expenses()

    while True:
        stdscr.clear()
        height, width = stdscr.getmaxyx()

        if width < 60:
            stdscr.addstr(
                2,
                2,
                "✖ Terminal too small! Resize & restart.",
                curses.color_pair(1) | curses.A_BOLD,
            )
            stdscr.refresh()
            stdscr.getch()
            break

        # Main menu border
        border_width = 50
        draw_border(stdscr, 0, 2, 12, border_width)
        header = "📊 EXPENSE TRACKER"
        stdscr.addstr(
            1,
            max(4, (border_width - len(header)) // 2 + 2),
            header,
            curses.color_pair(5) | curses.A_BOLD,
        )
        stdscr.addstr(2, 4, "─" * (border_width - 8), curses.color_pair(5))

        stdscr.addstr(4, 4, "➤ 1. Add Expenses", curses.color_pair(4) | curses.A_BOLD)
        stdscr.addstr(
            5, 4, "➤ 2. Delete Expenses", curses.color_pair(4) | curses.A_BOLD
        )
        stdscr.addstr(6, 4, "✖ 3. Exit", curses.color_pair(1) | curses.A_BOLD)

        if width > 80:
            stdscr.addstr(
                4, 55, "📋 YOUR EXPENSES", curses.color_pair(5) | curses.A_BOLD
            )
            stdscr.addstr(5, 55, "─" * 20, curses.color_pair(5))
            max_displayable = max(0, height - 8)
            for i, expense in enumerate(expenses[:max_displayable], start=1):
                date = expense[0].ljust(12)
                category = expense[1].ljust(15)
                amount = f"₹{expense[2]}".ljust(8)
                stdscr.addstr(6 + i, 55, f"▸ {i}. {date} | {category} | {amount}")
            if not expenses:
                stdscr.addstr(6, 55, "○ No expenses added yet.", curses.color_pair(1))

        stdscr.addstr(9, 4, "─" * (border_width - 8), curses.color_pair(5))
        stdscr.addstr(
            10, 4, "➔ Enter your choice: ", curses.color_pair(3) | curses.A_BOLD
        )
        stdscr.refresh()

        choice = stdscr.getch()

        if choice == ord("1"):  # Add Expenses
            while True:
                stdscr.clear()
                draw_border(stdscr, 0, 2, 15, border_width)
                header = "➕ ADD EXPENSE"
                stdscr.addstr(
                    1,
                    max(4, (border_width - len(header)) // 2 + 2),
                    header,
                    curses.color_pair(5) | curses.A_BOLD,
                )
                stdscr.addstr(2, 4, "─" * (border_width - 8), curses.color_pair(5))

                date_label = "📅 Date (DD-MM-YYYY): "
                category_label = "🏷️ Category: ".ljust(len(date_label))
                amount_label = "💲 Amount (₹): ".ljust(len(date_label))

                date = get_valid_date(stdscr, 4, 4, date_label)
                category = get_input(stdscr, 6, 4, category_label)
                amount = get_valid_amount(stdscr, 8, 4, amount_label)

                expenses.append([date, category, amount])
                expenses = sorted(
                    expenses, key=lambda x: datetime.datetime.strptime(x[0], "%d-%m-%Y")
                )
                save_expenses(expenses)

                stdscr.addstr(11, 4, "✔ Expense Added!", curses.color_pair(2))
                stdscr.addstr(
                    12, 4, "Add another? (y/n): ", curses.color_pair(3) | curses.A_BOLD
                )
                stdscr.addstr(13, 4, "─" * (border_width - 8), curses.color_pair(5))
                stdscr.refresh()
                response = stdscr.getch()
                if response not in [ord("y"), ord("Y")]:
                    break

        elif choice == ord("2"):  # Delete Expenses
            stdscr.clear()
            max_height, _ = stdscr.getmaxyx()
            max_expenses_displayable = max(
                0, max_height - 8
            )  # 8 rows for header, dividers, prompt, etc.
            display_expenses = expenses[:max_expenses_displayable]
            border_height = 8 + len(display_expenses)
            draw_border(stdscr, 0, 2, border_height, border_width)
            header = "🗑️ DELETE EXPENSES"
            stdscr.addstr(
                1,
                max(4, (border_width - len(header)) // 2 + 2),
                header,
                curses.color_pair(5) | curses.A_BOLD,
            )
            stdscr.addstr(2, 4, "─" * (border_width - 8), curses.color_pair(5))

            if not expenses:
                stdscr.addstr(4, 4, "○ No expenses to delete.", curses.color_pair(1))
                stdscr.addstr(5, 4, "─" * (border_width - 8), curses.color_pair(5))
                stdscr.refresh()
                stdscr.getch()
                continue

            for i, expense in enumerate(display_expenses, start=1):
                date = expense[0].ljust(12)
                category = expense[1].ljust(15)
                amount = f"₹{expense[2]}".ljust(8)
                stdscr.addstr(4 + i, 4, f"▸ {i}. {date} | {category} | {amount}")

            prompt_row = 4 + len(display_expenses) + 1
            prompt = "➔ Enter numbers (e.g., 1,3,5): "
            stdscr.addstr(prompt_row, 4, "─" * (border_width - 8), curses.color_pair(5))
            stdscr.addstr(
                prompt_row + 1,
                max(4, (border_width - len(prompt)) // 2 + 2),
                prompt,
                curses.color_pair(3) | curses.A_BOLD,
            )
            stdscr.refresh()
            indices_input = get_input(
                stdscr,
                prompt_row + 1,
                max(4, (border_width - len(prompt)) // 2 + 2) + len(prompt),
                "",
                50,
            )

            if not indices_input:
                stdscr.addstr(
                    prompt_row + 2, 4, "✖ No input provided!", curses.color_pair(1)
                )
                stdscr.addstr(
                    prompt_row + 3, 4, "─" * (border_width - 8), curses.color_pair(5)
                )
                stdscr.refresh()
                stdscr.getch()
                continue

            try:
                indices = []
                for idx in indices_input.split(","):
                    idx = idx.strip()
                    if idx.isdigit():
                        idx_int = int(idx) - 1
                        if 0 <= idx_int < len(expenses):
                            indices.append(idx_int)
                indices = sorted(set(indices), reverse=True)

                if not indices:
                    stdscr.addstr(
                        prompt_row + 2,
                        4,
                        "✖ No valid indices provided!",
                        curses.color_pair(1),
                    )
                    stdscr.addstr(
                        prompt_row + 3,
                        4,
                        "─" * (border_width - 8),
                        curses.color_pair(5),
                    )
                    stdscr.refresh()
                    stdscr.getch()
                    continue

                deleted = 0
                for idx in indices:
                    del expenses[idx]
                    deleted += 1

                save_expenses(expenses)

                stdscr.clear()
                max_expenses_displayable = max(0, max_height - 8)
                display_expenses = expenses[:max_expenses_displayable]
                border_height = 8 + len(display_expenses)
                draw_border(stdscr, 0, 2, border_height, border_width)
                stdscr.addstr(
                    1,
                    max(4, (border_width - len(header)) // 2 + 2),
                    header,
                    curses.color_pair(5) | curses.A_BOLD,
                )
                stdscr.addstr(2, 4, "─" * (border_width - 8), curses.color_pair(5))
                for i, expense in enumerate(display_expenses, start=1):
                    date = expense[0].ljust(12)
                    category = expense[1].ljust(15)
                    amount = f"₹{expense[2]}".ljust(8)
                    stdscr.addstr(4 + i, 4, f"▸ {i}. {date} | {category} | {amount}")
                message = f"✔ {deleted} expense(s) deleted!"
                stdscr.addstr(
                    4 + len(display_expenses) + 1,
                    4,
                    "─" * (border_width - 8),
                    curses.color_pair(5),
                )
                stdscr.addstr(
                    4 + len(display_expenses) + 2,
                    max(4, (border_width - len(message)) // 2 + 2),
                    message,
                    curses.color_pair(2),
                )
                stdscr.addstr(
                    4 + len(display_expenses) + 3,
                    4,
                    "─" * (border_width - 8),
                    curses.color_pair(5),
                )
            except Exception as e:
                stdscr.addstr(
                    prompt_row + 2, 4, f"✖ Error: {str(e)}", curses.color_pair(1)
                )
                stdscr.addstr(
                    prompt_row + 3, 4, "─" * (border_width - 8), curses.color_pair(5)
                )

            stdscr.refresh()
            stdscr.getch()

        elif choice == ord("3"):  # Exit
            break


# Run the program
curses.wrapper(main)
