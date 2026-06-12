/* ============================================
   SUPABASE CLIENT - Configuration
   ============================================ */

const SUPABASE_URL = 'https://xxxxx.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGci...';

const supabaseClient = supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY, {
  auth: {
    autoRefreshToken: true,
    persistSession: true,
    detectSessionInUrl: true
  }
});

async function getSession() {
  const { data: { session } } = await supabaseClient.auth.getSession();
  return session;
}

async function getCurrentUser() {
  const { data: { user } } = await supabaseClient.auth.getUser();
  return user;
}

async function getCurrentProfile() {
  const user = await getCurrentUser();
  if (!user) return null;

  const { data, error } = await supabaseClient
    .from('profiles')
    .select('*')
    .eq('id', user.id)
    .single();

  if (error) {
    console.error('Erreur profil:', error);
    return null;
  }

  return data;
}

async function requireAuth(redirectTo = 'connexion.html') {
  const session = await getSession();
  if (!session) {
    window.location.href = redirectTo;
    return false;
  }
  return true;
}

async function redirectIfAuth(redirectTo = 'mon-compte.html') {
  const session = await getSession();
  if (session) {
    window.location.href = redirectTo;
    return true;
  }
  return false;
}

if (typeof window !== 'undefined') {
  window.supabaseClient = supabaseClient;
  window.getSession = getSession;
  window.getCurrentUser = getCurrentUser;
  window.getCurrentProfile = getCurrentProfile;
  window.requireAuth = requireAuth;
  window.redirectIfAuth = redirectIfAuth;
}
