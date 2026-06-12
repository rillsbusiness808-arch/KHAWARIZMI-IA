/* ============================================
   AUTH SUPABASE - Système d'authentification complet
   ============================================ */

const AuthSupabase = {

  async register(userData) {
    try {
      const { data: authData, error: authError } = await supabaseClient.auth.signUp({
        email: userData.email,
        password: userData.password,
        options: {
          data: {
            first_name: userData.firstName,
            last_name: userData.lastName
          },
          emailRedirectTo: `${window.location.origin}/verifier-email.html`
        }
      });

      if (authError) {
        return { success: false, error: this.translateError(authError.message) };
      }

      if (authData.user) {
        const { error: profileError } = await supabaseClient
          .from('profiles')
          .update({
            phone: userData.phone,
            wilaya: userData.wilaya,
            telegram: userData.telegram,
            birthdate: userData.birthdate,
            level: userData.level,
            newsletter: userData.newsletter
          })
          .eq('id', authData.user.id);

        if (profileError) {
          console.error('Erreur profil:', profileError);
        }
      }

      return {
        success: true,
        user: authData.user,
        message: 'تم إرسال رابط التأكيد إلى بريدك الإلكتروني'
      };

    } catch (error) {
      return { success: false, error: error.message };
    }
  },

  async login(email, password) {
    try {
      const { data, error } = await supabaseClient.auth.signInWithPassword({
        email,
        password
      });

      if (error) {
        return { success: false, error: this.translateError(error.message) };
      }

      await supabaseClient
        .from('profiles')
        .update({ last_login: new Date().toISOString() })
        .eq('id', data.user.id);

      return { success: true, user: data.user, session: data.session };

    } catch (error) {
      return { success: false, error: error.message };
    }
  },

  async loginWithGoogle() {
    try {
      const { data, error } = await supabaseClient.auth.signInWithOAuth({
        provider: 'google',
        options: {
          redirectTo: `${window.location.origin}/mon-compte.html`
        }
      });

      if (error) {
        return { success: false, error: this.translateError(error.message) };
      }

      return { success: true, data };

    } catch (error) {
      return { success: false, error: error.message };
    }
  },

  async loginWithFacebook() {
    try {
      const { data, error } = await supabaseClient.auth.signInWithOAuth({
        provider: 'facebook',
        options: {
          redirectTo: `${window.location.origin}/mon-compte.html`
        }
      });

      if (error) {
        return { success: false, error: this.translateError(error.message) };
      }

      return { success: true, data };

    } catch (error) {
      return { success: false, error: error.message };
    }
  },

  async logout() {
    try {
      const { error } = await supabaseClient.auth.signOut();
      if (error) throw error;
      window.location.href = 'index.html';
      return { success: true };
    } catch (error) {
      return { success: false, error: error.message };
    }
  },

  async resetPassword(email) {
    try {
      const { error } = await supabaseClient.auth.resetPasswordForEmail(email, {
        redirectTo: `${window.location.origin}/reinitialiser-mot-de-passe.html`
      });

      if (error) {
        return { success: false, error: this.translateError(error.message) };
      }

      return {
        success: true,
        message: 'تم إرسال رابط إعادة تعيين كلمة المرور إلى بريدك الإلكتروني'
      };

    } catch (error) {
      return { success: false, error: error.message };
    }
  },

  async updatePassword(newPassword) {
    try {
      const { error } = await supabaseClient.auth.updateUser({
        password: newPassword
      });

      if (error) {
        return { success: false, error: this.translateError(error.message) };
      }

      return {
        success: true,
        message: 'تم تحديث كلمة المرور بنجاح'
      };

    } catch (error) {
      return { success: false, error: error.message };
    }
  },

  async resendVerificationEmail(email) {
    try {
      const { error } = await supabaseClient.auth.resend({
        type: 'signup',
        email: email
      });

      if (error) {
        return { success: false, error: this.translateError(error.message) };
      }

      return {
        success: true,
        message: 'تم إعادة إرسال رابط التأكيد'
      };

    } catch (error) {
      return { success: false, error: error.message };
    }
  },

  async updateProfile(updates) {
    try {
      const user = await getCurrentUser();
      if (!user) {
        return { success: false, error: 'يجب تسجيل الدخول' };
      }

      const { data, error } = await supabaseClient
        .from('profiles')
        .update({
          ...updates,
          updated_at: new Date().toISOString()
        })
        .eq('id', user.id)
        .select()
        .single();

      if (error) {
        return { success: false, error: error.message };
      }

      return { success: true, profile: data };

    } catch (error) {
      return { success: false, error: error.message };
    }
  },

  translateError(error) {
    const errors = {
      'Invalid login credentials': 'البريد الإلكتروني أو كلمة المرور غير صحيحة',
      'Email not confirmed': 'يرجى تأكيد بريدك الإلكتروني أولاً',
      'User already registered': 'هذا البريد مسجل بالفعل',
      'Password should be at least 6 characters': 'كلمة المرور يجب أن تحتوي على 6 أحرف على الأقل',
      'Unable to validate email address: invalid format': 'صيغة البريد الإلكتروني غير صحيحة',
      'For security purposes, you can only request this once every 60 seconds': 'لأسباب أمنية، يمكنك المحاولة مرة كل 60 ثانية',
      'Email rate limit exceeded': 'تم تجاوز حد الرسائل، حاول لاحقاً'
    };

    return errors[error] || error;
  }
};

if (typeof window !== 'undefined') {
  window.AuthSupabase = AuthSupabase;
}
