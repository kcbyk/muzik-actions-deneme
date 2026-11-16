# GitHub Actions ile izinli ses hazırlama demosu

## Kurulum
1. Bu dosyaları **public** bir GitHub deposunun `main` dalına yerleştir. Actions'ın bu depoda etkin olduğunu doğrula. Varsayılan dalın `main` değilse index.html içindeki `ref` değerini değiştir.
2. `.github/workflows/download.yml` Actions sekmesinde görünmeli. GitHub Pages veya başka bir statik sunucuda `index.html`'i HTTPS ile sun.
3. Kendi hesabında yalnız bu depoya erişebilen, kısa ömürlü fine-grained kişisel erişim token'ı oluştur; **Actions: Read and write** izni ver. Releases okumak için public repo yeterlidir. Form token'ı yalnız çalışma zamanında bellekte kullanır; kodun içine koyma veya localStorage'a kaydetme. Bu yaklaşım sadece token sahibi kişilerin kendi deposuna istek atması için uygundur.
4. Arama veya HTTPS YouTube URL'si gir ve yalnız hak sahibi olduğun/izin aldığın bir içerikle dene. `ytsearch1` ilk sonucu seçer; yanlış sonuç seçebilir. Başarılı iş akışından sonra `request-<uuid>` release'i ve `track.mp3` oluşur.

## Sınırlar ve önemli uyarılar
- Genel kullanıcılar için sıfır-backend ortamında ortak bir GitHub token'ı saklamak **güvenli değildir**. Herkese açık kullanımda auth ve hız limiti için bir serverless proxy gerekir; free tier varsa dahi limit ve ücretlendirme sağlayıcıya göre değişir.
- Workflow ilk kez ve varsayılan dalda mevcut olmalıdır. Bu örnekte tarayıcı, `main` dalını tetikler. Bir isteğin bitmesi saniyeler-dakikalar sürebilir; gerçek zamanlı yayın değildir.
- Depo/release public olmalıdır; public dosyalar herkese açıktır. Private GitHub Release bağlantıları `<audio>` öğesinde GitHub token'ını güvenli şekilde ekleyemediğinden çalışmayabilir.
- Tarayıcının autoplay kuralları nedeniyle oynatma kullanıcının düğmeye basmasını gerektirebilir. Tarayıcı/GitHub yönlendirme ve içerik politikaları çalışmayı etkileyebilir.
- GitHub Actions, API, depolama, bant genişliği ve Releases kullanım sınırları vardır. Bu tasarım büyük ölçekli depolama, yayın servisi veya ücretsiz-sınırsız hosting olarak uygun değildir; GitHub politikaları ve hak sahiplerinin şartları geçerlidir.
- Kod 10 dakikalık süre ve 80 MiB kaynak boyutu üst sınırı uygular. Hatalarda Actions loglarına bak. Eski release'leri ve etiketlerini el ile sil; otomatik temizleme bu demoda yok.
- `yt-dlp` sürüm değişiklikleri, YouTube bot kontrolleri veya kısıtları nedeniyle başarısız olabilir. DRM, kimlik doğrulama veya platform kısıtlarını aşmaya yönelik özellik eklenmemiştir.
