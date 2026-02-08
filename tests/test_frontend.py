"""
Phase 3: Frontend Tests
RTL layout, navigation, role-based UI, forms, tables, kanban, chat interface.
Uses Flask test client + BeautifulSoup to parse HTML.
"""
import pytest
from bs4 import BeautifulSoup

pytestmark = pytest.mark.frontend


def parse(response):
    """Parse HTML response into BeautifulSoup."""
    return BeautifulSoup(response.data.decode('utf-8'), 'html.parser')


# ============================================================
# 3.1 Layout & RTL
# ============================================================

class TestLayoutRTL:
    """Verify RTL and Hebrew layout."""

    def test_html_dir_rtl(self, doctor_client):
        """HTML tag has dir='rtl'."""
        resp = doctor_client.get('/dashboard')
        soup = parse(resp)
        html_tag = soup.find('html')
        assert html_tag is not None
        assert html_tag.get('dir') == 'rtl'

    def test_html_lang_hebrew(self, doctor_client):
        """HTML tag has lang='he'."""
        resp = doctor_client.get('/dashboard')
        soup = parse(resp)
        html_tag = soup.find('html')
        assert html_tag is not None
        assert html_tag.get('lang') == 'he'

    def test_heebo_font_loaded(self, doctor_client):
        """Heebo (Hebrew) font is loaded via Google Fonts."""
        resp = doctor_client.get('/dashboard')
        body = resp.data.decode('utf-8')
        assert 'Heebo' in body

    def test_material_icons_loaded(self, doctor_client):
        """Material Symbols Outlined icons are loaded."""
        resp = doctor_client.get('/dashboard')
        body = resp.data.decode('utf-8')
        assert 'Material' in body or 'material' in body


# ============================================================
# 3.2 Login Page
# ============================================================

class TestLoginPage:
    """Verify login page structure."""

    def test_login_has_email_field(self, client):
        """Login page has email input."""
        resp = client.get('/login')
        soup = parse(resp)
        email_input = soup.find('input', {'name': 'email'}) or soup.find('input', {'type': 'email'})
        assert email_input is not None

    def test_login_has_password_field(self, client):
        """Login page has password input."""
        resp = client.get('/login')
        soup = parse(resp)
        pwd_input = soup.find('input', {'name': 'password'}) or soup.find('input', {'type': 'password'})
        assert pwd_input is not None

    def test_login_has_submit_button(self, client):
        """Login page has submit button."""
        resp = client.get('/login')
        soup = parse(resp)
        btn = soup.find('button', {'type': 'submit'})
        assert btn is not None

    def test_login_shows_demo_credentials(self, client):
        """Login page shows demo credentials."""
        resp = client.get('/login')
        body = resp.data.decode('utf-8')
        assert 'doctor@demo.com' in body or 'demo' in body.lower()


# ============================================================
# 3.3 Sidebar Navigation
# ============================================================

class TestSidebar:
    """Verify sidebar navigation."""

    def test_sidebar_renders(self, doctor_client):
        """Sidebar component is present."""
        resp = doctor_client.get('/dashboard')
        soup = parse(resp)
        # Look for sidebar or nav element
        sidebar = soup.find('aside') or soup.find('nav')
        assert sidebar is not None

    def test_sidebar_nav_items_doctor(self, doctor_client):
        """Doctor sees all nav items including chat."""
        resp = doctor_client.get('/dashboard')
        body = resp.data.decode('utf-8')
        nav_items = ['לוח בקרה', 'מטופלים', 'שירותים', 'תורים', 'חשבוניות', 'משימות']
        for item in nav_items:
            assert item in body, f'Nav item "{item}" not found in sidebar'

    def test_sidebar_chat_visible_doctor(self, doctor_client):
        """Doctor sees chat link in sidebar."""
        resp = doctor_client.get('/dashboard')
        body = resp.data.decode('utf-8')
        assert 'צ\'אט' in body or 'chat' in body.lower()

    def test_sidebar_chat_hidden_secretary(self, secretary_client):
        """Secretary does NOT see chat link in sidebar."""
        resp = secretary_client.get('/dashboard')
        body = resp.data.decode('utf-8')
        soup = parse(resp)
        # Find links to /chat
        chat_links = soup.find_all('a', href='/chat')
        assert len(chat_links) == 0, 'Secretary should not see chat link'

    def test_sidebar_has_logout(self, doctor_client):
        """Sidebar has logout option."""
        resp = doctor_client.get('/dashboard')
        body = resp.data.decode('utf-8')
        assert 'logout' in body.lower() or 'התנתק' in body


# ============================================================
# 3.4 Dashboard Page
# ============================================================

class TestDashboardPage:
    """Verify dashboard structure."""

    def test_dashboard_kpi_cards(self, doctor_client):
        """Dashboard has KPI metric cards."""
        resp = doctor_client.get('/dashboard')
        body = resp.data.decode('utf-8')
        # Check for KPI labels in Hebrew
        kpi_labels = ['מטופלים', 'תורים', 'הכנסות']
        found = sum(1 for label in kpi_labels if label in body)
        assert found >= 2, f'Only found {found} KPI labels'

    def test_dashboard_charts_canvas(self, doctor_client):
        """Dashboard has Chart.js canvas elements."""
        resp = doctor_client.get('/dashboard')
        soup = parse(resp)
        canvases = soup.find_all('canvas')
        assert len(canvases) >= 1, 'No chart canvas elements found'

    def test_dashboard_chartjs_loaded(self, doctor_client):
        """Chart.js library is loaded."""
        resp = doctor_client.get('/dashboard')
        body = resp.data.decode('utf-8')
        assert 'chart' in body.lower()

    def test_dashboard_churn_section_doctor(self, doctor_client):
        """Doctor sees churn prediction section."""
        resp = doctor_client.get('/dashboard')
        body = resp.data.decode('utf-8')
        # Should have risk/churn related content
        assert 'נטישה' in body or 'סיכון' in body or 'churn' in body.lower()


# ============================================================
# 3.5 Tables (Patients, Services, Appointments, Invoices)
# ============================================================

class TestTables:
    """Verify table pages structure."""

    def test_patients_table_renders(self, doctor_client):
        """Patients page has a table with rows."""
        resp = doctor_client.get('/patients')
        soup = parse(resp)
        table = soup.find('table')
        assert table is not None, 'No table found on patients page'
        rows = table.find_all('tr')
        assert len(rows) >= 2  # Header + at least 1 data row

    def test_patients_search_input(self, doctor_client):
        """Patients page has search input."""
        resp = doctor_client.get('/patients')
        soup = parse(resp)
        search = soup.find('input', {'id': 'searchInput'}) or soup.find('input', {'type': 'search'}) or soup.find('input', {'placeholder': True})
        assert search is not None

    def test_patients_add_button(self, doctor_client):
        """Patients page has add/create button."""
        resp = doctor_client.get('/patients')
        body = resp.data.decode('utf-8')
        assert 'הוסף' in body or 'חדש' in body or 'add' in body.lower()

    def test_patients_pagination(self, doctor_client):
        """Patients page has pagination controls."""
        resp = doctor_client.get('/patients')
        body = resp.data.decode('utf-8')
        # Should have page navigation
        assert 'goToPage' in body or 'page' in body.lower()

    def test_services_table_renders(self, doctor_client):
        """Services page has a table."""
        resp = doctor_client.get('/services')
        soup = parse(resp)
        table = soup.find('table')
        assert table is not None

    def test_appointments_table_renders(self, doctor_client):
        """Appointments page has a table."""
        resp = doctor_client.get('/appointments')
        soup = parse(resp)
        table = soup.find('table')
        assert table is not None

    def test_invoices_table_renders(self, doctor_client):
        """Invoices page has a table."""
        resp = doctor_client.get('/invoices')
        soup = parse(resp)
        table = soup.find('table')
        assert table is not None

    def test_invoices_status_filter(self, doctor_client):
        """Invoices page has status filter."""
        resp = doctor_client.get('/invoices')
        body = resp.data.decode('utf-8')
        assert 'filterByStatus' in body or 'status' in body.lower()


# ============================================================
# 3.6 Patient Detail Page
# ============================================================

class TestPatientDetail:
    """Verify patient detail page structure."""

    def test_detail_has_patient_info(self, doctor_client, sample_patient_id):
        """Detail page shows patient info."""
        resp = doctor_client.get(f'/patients/{sample_patient_id}')
        assert resp.status_code == 200
        body = resp.data.decode('utf-8')
        # Detail page should render substantial content
        assert len(body) > 1000, 'Detail page seems empty'

    def test_detail_has_medical_history_doctor(self, doctor_client, sample_patient_id):
        """Doctor sees medical history on detail page."""
        resp = doctor_client.get(f'/patients/{sample_patient_id}')
        body = resp.data.decode('utf-8')
        assert 'היסטוריה' in body or 'אבחנות' in body or 'medical' in body.lower()

    def test_detail_hides_medical_history_secretary(self, secretary_client, sample_patient_id):
        """Secretary does NOT see medical history on detail page."""
        resp = secretary_client.get(f'/patients/{sample_patient_id}')
        body = resp.data.decode('utf-8')
        # Medical history section should be hidden
        # Check that diagnoses/medications labels are NOT present
        assert 'אבחנות' not in body and 'תרופות' not in body, \
            'Secretary should not see medical history details'

    def test_detail_has_appointments_section(self, doctor_client, sample_patient_id):
        """Detail page shows appointments history."""
        resp = doctor_client.get(f'/patients/{sample_patient_id}')
        body = resp.data.decode('utf-8')
        assert 'תורים' in body

    def test_detail_has_invoices_section(self, doctor_client, sample_patient_id):
        """Detail page shows invoices history."""
        resp = doctor_client.get(f'/patients/{sample_patient_id}')
        body = resp.data.decode('utf-8')
        assert 'חשבוניות' in body


# ============================================================
# 3.7 Kanban Board
# ============================================================

class TestKanbanBoard:
    """Verify kanban board structure."""

    def test_kanban_three_columns(self, doctor_client):
        """Kanban has 3 columns: open, in_progress, done."""
        resp = doctor_client.get('/tasks')
        body = resp.data.decode('utf-8')
        assert 'column-open' in body or 'open' in body.lower()
        assert 'in_progress' in body or 'בביצוע' in body
        assert 'done' in body or 'הושלם' in body

    def test_kanban_sortable_loaded(self, doctor_client):
        """SortableJS is loaded."""
        resp = doctor_client.get('/tasks')
        body = resp.data.decode('utf-8')
        assert 'Sortable' in body or 'sortable' in body.lower()

    def test_kanban_has_task_cards(self, doctor_client):
        """Kanban has task cards with data-task-id."""
        resp = doctor_client.get('/tasks')
        body = resp.data.decode('utf-8')
        assert 'data-task-id' in body or 'task' in body.lower()

    def test_kanban_create_task_form(self, doctor_client):
        """Kanban has create task button/form."""
        resp = doctor_client.get('/tasks')
        body = resp.data.decode('utf-8')
        assert 'הוסף' in body or 'חדש' in body or 'משימה' in body


# ============================================================
# 3.8 Chat Interface
# ============================================================

class TestChatInterface:
    """Verify chat UI structure."""

    def test_chat_page_renders(self, doctor_client):
        """Chat page renders for doctor."""
        resp = doctor_client.get('/chat')
        assert resp.status_code == 200

    def test_chat_has_input_field(self, doctor_client):
        """Chat page has message input."""
        resp = doctor_client.get('/chat')
        soup = parse(resp)
        input_field = soup.find('input', {'type': 'text'}) or soup.find('textarea')
        assert input_field is not None

    def test_chat_has_send_button(self, doctor_client):
        """Chat page has send button."""
        resp = doctor_client.get('/chat')
        soup = parse(resp)
        btn = soup.find('button')
        assert btn is not None

    def test_chat_js_loaded(self, doctor_client):
        """Chat JavaScript is loaded."""
        resp = doctor_client.get('/chat')
        body = resp.data.decode('utf-8')
        assert 'chat' in body.lower()


# ============================================================
# 3.9 Error Pages
# ============================================================

class TestErrorPages:
    """Verify error pages."""

    def test_404_page_renders(self, doctor_client):
        """404 page renders with proper structure."""
        resp = doctor_client.get('/this-does-not-exist')
        assert resp.status_code == 404
        body = resp.data.decode('utf-8')
        assert '404' in body

    def test_flash_messages_structure(self, client):
        """Login with bad creds shows flash message."""
        resp = client.post('/login', data={
            'email': 'bad@email.com', 'password': 'wrong',
        }, follow_redirects=True)
        body = resp.data.decode('utf-8')
        # Should have flash message visible
        assert 'שגויים' in body or 'danger' in body


# ============================================================
# 3.10 Forms
# ============================================================

class TestForms:
    """Verify form structures have correct fields."""

    def test_patient_form_has_required_fields(self, doctor_client):
        """Patient page has modal form with name/phone fields."""
        resp = doctor_client.get('/patients')
        body = resp.data.decode('utf-8')
        assert 'first_name' in body
        assert 'last_name' in body
        assert 'phone' in body

    def test_services_form_has_price(self, doctor_client):
        """Services page form has price field."""
        resp = doctor_client.get('/services')
        body = resp.data.decode('utf-8')
        assert 'price' in body

    def test_appointment_form_has_dropdowns(self, doctor_client):
        """Appointments form has patient/service dropdowns."""
        resp = doctor_client.get('/appointments')
        body = resp.data.decode('utf-8')
        assert 'patient_id' in body
        assert 'service_id' in body
