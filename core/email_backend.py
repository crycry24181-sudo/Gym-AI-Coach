# core/email_backend.py
import ssl
from django.core.mail.backends.smtp import EmailBackend


class FixedEmailBackend(EmailBackend):
    """
    Vá lỗi gửi mail Python 3.12+ (Phiên bản An Toàn - V2)
    """

    def open(self):
        if self.connection:
            return False
        try:
            self.connection = self.connection_class(self.host, self.port, timeout=self.timeout)

            # --- PHẦN SỬA LỖI ĐÃ CẬP NHẬT ---
            if self.use_tls:
                # Dùng lệnh getattr để lấy context an toàn (tránh lỗi AttributeError)
                context = getattr(self, 'ssl_context', None)

                # Nếu không có (None), ta tự tạo context mặc định
                if context is None:
                    context = ssl.create_default_context()

                self.connection.starttls(context=context)
            # --------------------------------

            if self.username and self.password:
                self.connection.login(self.username, self.password)
            return True
        except OSError:
            if not self.fail_silently:
                raise