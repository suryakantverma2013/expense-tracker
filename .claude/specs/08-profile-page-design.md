# Spec: Profile Page Design

## Overview
Step 8 delivers a fully polished, production-quality profile page and implements the edit-expense workflow that the `app.py` stub marks "coming in Step 8". By this point the profile page is functionally complete (Steps 4–7), but the visual design is minimal. This step introduces a dedicated `static/css/profile.css`, refines the layout into a card-based dashboard, turns the category breakdown into CSS progress-bar visualisation, and adds Edit buttons to each expense row backed by a real `GET/POST /expenses/<id>/edit` route and a corresponding query helper. The result is a page that looks finished and handles the full expense lifecycle: view, add, and edit.

## Depends on
- Step 1: Database setup (`users` and `expenses` tables, `get_db()`)
- Step 4: Profile page static HTML (template structure must exist)
- Step 5: Backend connection (`database/queries.py` with all four query helpers)
- Step 6: Date-filter profile (filter bar present; `profile.css` may already exist with filter styles)
- Step 7: Add expense (`insert_expense` helper exists; "Add Expense" button in the navbar and profile page)

## Routes
- `GET /expenses/<int:id>/edit` — render pre-filled edit form for one expense — logged-in only
- `POST /expenses/<int:id>/edit` — validate and update the expense row — logged-in only

## Database changes
No database changes. The `expenses` table already has all required columns.

## Templates
- **Create**: `templates/edit_expense.html`
  - Extends `base.html`
  - Form with `method="POST"` and `action="/expenses/<id>/edit"`
  - Same four fields as `add_expense.html` (`amount`, `category`, `date`, `description`), pre-populated with the current row's values
  - Submit button ("Save Changes") and a cancel link back to `/profile`
  - Display flash/error message when validation fails, retaining submitted values

- **Modify**: `templates/profile.html`
  - Wrap the entire page body in a two-column dashboard grid: a left **summary sidebar** (user card + stats + category breakdown) and a right **main panel** (filter bar + transaction table)
  - Category breakdown: replace the plain list with CSS progress bars — each row shows the category name, a `<div class="progress-bar">` whose `width` is set via an inline `style="width: {{ item.pct }}%"` (width only — no colour inline), and the formatted amount
  - Transaction table: add an "Edit" link at the end of each row pointing to `/expenses/<id>/edit`
  - Apply BEM-style CSS classes (`profile-card`, `stat-card`, `progress-bar`, `expense-row`, etc.) so the new stylesheet has clean hooks

## Files to change
- `app.py`
  - Replace the `GET /expenses/<int:id>/edit` stub with a full GET + POST handler:
    - GET: fetch the expense row by `id`; verify it belongs to `session["user_id"]`; render `edit_expense.html` with pre-filled values; 404 if not found or not owned
    - POST: validate same rules as add-expense; call `update_expense`; redirect to `url_for("profile")` on success; re-render form with error on failure
  - Both GET and POST must redirect unauthenticated users to `/login`
- `database/queries.py`
  - Add `get_expense_by_id(expense_id)` → dict or `None`
  - Add `update_expense(expense_id, amount, category, date, description)` → `None`
- `templates/profile.html` — layout and design changes described above
- `static/css/profile.css` — comprehensive profile-page styles (create if it does not exist yet)

## Files to create
- `templates/edit_expense.html`
- `static/css/profile.css` (if not already created in Step 6; if it exists, extend it)

## New dependencies
No new dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs — raw `sqlite3` only via `get_db()`
- Parameterised queries only — never string-format values into SQL
- Foreign keys PRAGMA must be enabled on every connection (already done in `get_db()`)
- Ownership check: before rendering or updating, confirm `expense.user_id == session["user_id"]`; return 404 otherwise (do not leak that the row exists)
- Validation rules for POST (same as Step 7):
  - `amount`: required, positive float > 0
  - `category`: required, one of the 7 fixed categories
  - `date`: required, valid `YYYY-MM-DD`
  - `description`: optional; strip whitespace; store `None` if blank
  - On any validation error re-render the form with the error and previously submitted values
- After successful update redirect to `url_for("profile")` — do NOT re-render the form
- Use CSS variables — never hardcode hex values; progress-bar `width` inline style is the only permitted inline style
- All templates extend `base.html`
- No inline styles except the single `width` on `.progress-bar` fill elements
- Currency must always display as ₹ — never £ or $
- `profile.css` must use only the design-system variables: `--ink`, `--paper`, `--accent`, `--accent-2`, `--danger`; no raw hex values
- Layout must remain usable at 375 px viewport width (mobile-first CSS)

## Definition of done
- [ ] Visiting `/expenses/<id>/edit` while logged out redirects to `/login`
- [ ] Visiting `/expenses/<id>/edit` for an expense owned by another user returns 404
- [ ] Visiting `/expenses/<id>/edit` while logged in and owning the expense returns 200 with all four fields pre-filled with the current values
- [ ] Submitting a valid edit redirects to `/profile` and the transaction list reflects the updated values
- [ ] Submitting an edit with a missing or zero amount re-renders the form with an error and retains previously submitted values
- [ ] Submitting an edit with an invalid category re-renders the form with an error
- [ ] Submitting an edit with an invalid date re-renders the form with an error
- [ ] The profile page displays a two-column dashboard layout (sidebar + main panel) at desktop viewport width
- [ ] The category breakdown section shows progress bars whose widths visually reflect each category's percentage of total spend
- [ ] Each row in the transaction table has an "Edit" link that navigates to the correct `/expenses/<id>/edit` URL
- [ ] No hex colour values appear in `profile.css` or `profile.html` — only CSS custom properties
- [ ] The page renders without layout breakage at 375 px viewport width
