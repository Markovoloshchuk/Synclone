import React, { useEffect, useState } from 'react';
import { createRoot } from 'react-dom/client';
import './style.css';

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000';

async function request(path, options = {}, token = '') {
  const response = await fetch(`${API}${path}`, {
    ...options,
    headers: { 'Content-Type': 'application/json', ...(token ? { Authorization: `Bearer ${token}` } : {}), ...(options.headers || {}) },
  });
  const data = response.status === 204 ? null : await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.detail || `Request failed (${response.status})`);
  return data;
}

function App() {
  const [token, setToken] = useState(() => localStorage.getItem('synclone_token') || '');
  const [user, setUser] = useState(null);
  const [mode, setMode] = useState('login');
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');
  const [busy, setBusy] = useState(false);
  const [backups, setBackups] = useState([]);
  const [users, setUsers] = useState([]);
  const [form, setForm] = useState({ email: '', password: '', full_name: '' });
  const [backupForm, setBackupForm] = useState({ clone_identifier: '', resident_name: '', memory_payload_hash: '' });

  const field = (key, value) => setForm(prev => ({ ...prev, [key]: value }));
  const backupField = (key, value) => setBackupForm(prev => ({ ...prev, [key]: value }));

  async function refresh(currentToken = token, currentUser = user) {
    const me = await request('/api/v1/auth/me', {}, currentToken);
    setUser(me);
    const ownBackups = await request('/api/v1/clones/backups/', {}, currentToken);
    setBackups(ownBackups);
    if (me.role === 'admin') setUsers(await request('/api/v1/admin/users', {}, currentToken));
  }

  useEffect(() => {
    if (token) refresh(token).catch(() => { localStorage.removeItem('synclone_token'); setToken(''); setUser(null); });
  }, [token]);

  async function submitAuth(event) {
    event.preventDefault(); setError(''); setNotice(''); setBusy(true);
    try {
      if (mode === 'register') {
        await request('/api/v1/auth/register', { method: 'POST', body: JSON.stringify(form) });
        setNotice('Обліковий запис створено. Тепер увійдіть.');
        setMode('login');
      } else {
        const data = await request('/api/v1/auth/login', { method: 'POST', body: JSON.stringify({ email: form.email, password: form.password }) });
        localStorage.setItem('synclone_token', data.access_token);
        setToken(data.access_token); setUser(data.user);
      }
    } catch (e) { setError(e.message); } finally { setBusy(false); }
  }

  async function createBackup(event) {
    event.preventDefault(); setError(''); setNotice(''); setBusy(true);
    try {
      await request('/api/v1/clones/backups/', { method: 'POST', body: JSON.stringify(backupForm) }, token);
      setBackupForm({ clone_identifier: '', resident_name: '', memory_payload_hash: '' });
      setNotice('Запис резервної копії створено.');
      await refresh();
    } catch (e) { setError(e.message); } finally { setBusy(false); }
  }

  async function updateUser(id, key, value) {
    setError(''); setNotice('');
    try {
      await request(`/api/v1/admin/users/${id}/${key}?${key === 'role' ? `role=${encodeURIComponent(value)}` : `is_active=${value}`}`, { method: 'PATCH' }, token);
      await refresh();
      setNotice('Дані користувача оновлено.');
    } catch (e) { setError(e.message); }
  }

  function logout() {
    localStorage.removeItem('synclone_token'); setToken(''); setUser(null); setBackups([]); setUsers([]);
  }

  if (!token || !user) return <main className="auth-layout">
    <section className="brand-panel"><div className="logo">S<span>.</span></div><p className="eyebrow">CLONE MEMORY MANAGEMENT</p><h1>Твої дані.<br/>Під твоїм контролем.</h1><p className="muted">Synclone — простий простір для обліку резервних копій клонів.</p><div className="decorative-orb"/></section>
    <section className="auth-panel"><div className="auth-card"><p className="eyebrow">{mode === 'login' ? 'З РАДІСТЮ ЗНОВУ БАЧИМО' : 'ПРИЄДНУЙСЯ ДО SYNCLONE'}</p><h2>{mode === 'login' ? 'Вхід до системи' : 'Створити акаунт'}</h2><p className="muted">{mode === 'login' ? 'Введи облікові дані, щоб продовжити.' : 'Реєстрація доступна для звичайних користувачів.'}</p>
      {error && <div className="alert error">{error}</div>}{notice && <div className="alert success">{notice}</div>}
      <form onSubmit={submitAuth} className="stack">
        {mode === 'register' && <label>Повне ім’я<input required maxLength="150" value={form.full_name} onChange={e => field('full_name', e.target.value)} placeholder="Як до тебе звертатися"/></label>}
        <label>Email<input required type="email" value={form.email} onChange={e => field('email', e.target.value)} placeholder="you@example.com"/></label>
        <label>Пароль<input required type="password" minLength={mode === 'register' ? 8 : 1} value={form.password} onChange={e => field('password', e.target.value)} placeholder={mode === 'register' ? 'Не менше 8 символів' : 'Твій пароль'}/></label>
        <button disabled={busy} className="primary">{busy ? 'Зачекай…' : mode === 'login' ? 'Увійти' : 'Зареєструватися'}</button>
      </form><p className="switch">{mode === 'login' ? 'Ще немає акаунта?' : 'Вже маєш акаунт?'} <button className="text-button" onClick={() => { setMode(mode === 'login' ? 'register' : 'login'); setError(''); setNotice(''); }}>{mode === 'login' ? 'Реєстрація' : 'Увійти'}</button></p>
      <p className="footnote">Адміністратор створюється під час першого запуску API зі змінних середовища.</p></div></section>
  </main>;

  return <div className="app-shell"><aside className="sidebar"><div className="logo">S<span>.</span> <small>synclone</small></div><div className="side-label">РОБОЧИЙ ПРОСТІР</div><div className="side-item active">▦ <span>Огляд</span></div>{user.role === 'admin' && <div className="side-item">♙ <span>Користувачі</span><b>{users.length}</b></div>}<div className="side-bottom"><div className="avatar">{user.full_name?.slice(0,1).toUpperCase()}</div><div className="profile"><strong>{user.full_name}</strong><small>{user.role === 'admin' ? 'Адміністратор' : 'Користувач'}</small></div><button title="Вийти" className="logout" onClick={logout}>↗</button></div></aside>
    <main className="dashboard"><header className="topbar"><div><span className="muted">Робочий простір /</span> Огляд</div><div className="user-chip"><span className="online-dot"/> {user.email}</div></header>
      <section className="welcome"><div><p className="eyebrow">ПАНЕЛЬ КЕРУВАННЯ</p><h1>{user.role === 'admin' ? 'Вітаємо, адміністраторе' : `Вітаємо, ${user.full_name.split(' ')[0]}`} 👋</h1><p className="muted">Керуй резервними копіями та стеж за їхнім станом.</p></div><span className="role-pill">{user.role === 'admin' ? 'ADMIN ACCESS' : 'USER ACCESS'}</span></section>
      {error && <div className="alert error">{error}</div>}{notice && <div className="alert success">{notice}</div>}
      <section className="stats"><article className="stat-card"><span className="stat-icon violet">▤</span><span className="muted">Мої резервні копії</span><strong>{backups.length}</strong><small>Записів у твоєму просторі</small></article><article className="stat-card"><span className="stat-icon green">✓</span><span className="muted">Статус сервісу</span><strong className="status-text">Активний</strong><small>API доступне</small></article>{user.role === 'admin' && <article className="stat-card"><span className="stat-icon blue">♙</span><span className="muted">Усього користувачів</span><strong>{users.length}</strong><small>Зареєстрованих акаунтів</small></article>}</section>
      <section className="content-grid"><article className="panel"><div className="panel-head"><div><h2>Створити резервну копію</h2><p className="muted">Додай метадані нового запису.</p></div><span className="panel-symbol">＋</span></div><form className="stack" onSubmit={createBackup}><label>Ідентифікатор клона<input required maxLength="100" value={backupForm.clone_identifier} onChange={e => backupField('clone_identifier', e.target.value)} placeholder="clone-001"/></label><label>Ім’я мешканця<input required maxLength="150" value={backupForm.resident_name} onChange={e => backupField('resident_name', e.target.value)} placeholder="Ім’я"/></label><label>Хеш даних<input required maxLength="255" value={backupForm.memory_payload_hash} onChange={e => backupField('memory_payload_hash', e.target.value)} placeholder="SHA-256 або інший хеш"/></label><button className="primary" disabled={busy}>Зберегти запис</button></form><p className="footnote">Ця версія зберігає метадані та хеш, а не сам файл резервної копії.</p></article>
      <article className="panel"><div className="panel-head"><div><h2>Останні записи</h2><p className="muted">Тільки твої резервні копії</p></div><span className="count-pill">{backups.length} записів</span></div>{backups.length ? <div className="backup-list">{backups.slice(0,8).map(b => <div className="backup-row" key={b.id}><div className="backup-icon">▤</div><div className="backup-info"><strong>{b.clone_identifier}</strong><small>{b.resident_name} · {new Date(b.created_at).toLocaleString('uk-UA')}</small></div><span className="status-pill">{b.status}</span></div>)}</div> : <div className="empty"><div>▤</div><strong>Поки немає записів</strong><p className="muted">Створи перший запис у формі ліворуч.</p></div>}</article></section>
      {user.role === 'admin' && <section className="panel users-panel"><div className="panel-head"><div><h2>Керування користувачами</h2><p className="muted">Зміна ролей та доступу до системи.</p></div><span className="count-pill">{users.length} акаунтів</span></div><div className="table-wrap"><table><thead><tr><th>Користувач</th><th>Роль</th><th>Стан</th><th>Дії</th></tr></thead><tbody>{users.map(u => <tr key={u.id}><td><strong>{u.full_name}</strong><small className="table-email">{u.email}</small></td><td><select value={u.role} disabled={u.id === user.id} onChange={e => updateUser(u.id, 'role', e.target.value)}><option value="user">Користувач</option><option value="admin">Адміністратор</option></select></td><td><span className={u.is_active ? 'active-label' : 'inactive-label'}>{u.is_active ? 'Активний' : 'Заблокований'}</span></td><td><button className="secondary small" disabled={u.id === user.id} onClick={() => updateUser(u.id, 'active', !u.is_active)}>{u.is_active ? 'Заблокувати' : 'Розблокувати'}</button></td></tr>)}</tbody></table></div></section>}
      <footer>Synclone <span>•</span> Безпечний простір керування резервними копіями</footer>
    </main></div>;
}

createRoot(document.getElementById('root')).render(<App />);
