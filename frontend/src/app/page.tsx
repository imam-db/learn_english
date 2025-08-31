export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-16">
        <div className="text-center">
          <h1 className="text-4xl md:text-6xl font-bold text-gray-900 mb-6">
            English Learning Platform
          </h1>
          <p className="text-xl md:text-2xl text-gray-600 mb-8 max-w-3xl mx-auto">
            Bank Soal + Buku Digital Bahasa Inggris
          </p>
          <p className="text-lg text-gray-500 mb-12 max-w-2xl mx-auto">
            Belajar bahasa Inggris dengan pelajaran interaktif dan bank soal komprehensif. 
            Dirancang khusus untuk pelajar Indonesia dengan level CEFR A1-B2.
          </p>
          
          <div className="grid md:grid-cols-3 gap-8 max-w-4xl mx-auto mb-12">
            <div className="bg-white rounded-lg shadow-lg p-6">
              <div className="text-3xl mb-4">📚</div>
              <h3 className="text-xl font-semibold mb-2">Interactive Lessons</h3>
              <p className="text-gray-600">
                Pelajaran terstruktur dengan penjelasan bilingual (Indonesia/English)
              </p>
            </div>
            
            <div className="bg-white rounded-lg shadow-lg p-6">
              <div className="text-3xl mb-4">❓</div>
              <h3 className="text-xl font-semibold mb-2">Question Bank</h3>
              <p className="text-gray-600">
                Bank soal komprehensif dengan berbagai jenis pertanyaan dan penjelasan detail
              </p>
            </div>
            
            <div className="bg-white rounded-lg shadow-lg p-6">
              <div className="text-3xl mb-4">📊</div>
              <h3 className="text-xl font-semibold mb-2">Progress Tracking</h3>
              <p className="text-gray-600">
                Sistem pelacakan kemajuan dengan Spaced Repetition System (SRS)
              </p>
            </div>
          </div>
          
          <div className="space-y-4 sm:space-y-0 sm:space-x-4 sm:flex sm:justify-center">
            <button className="w-full sm:w-auto bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-8 rounded-lg transition duration-200">
              Mulai Belajar
            </button>
            <button className="w-full sm:w-auto border border-blue-600 text-blue-600 hover:bg-blue-50 font-semibold py-3 px-8 rounded-lg transition duration-200">
              Pelajari Lebih Lanjut
            </button>
          </div>
        </div>
      </div>
      
      <div className="bg-white py-16">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-3xl font-bold text-gray-900 mb-8">
            Fitur Utama Platform
          </h2>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 max-w-6xl mx-auto">
            <div className="p-4">
              <div className="text-2xl mb-3">🎯</div>
              <h4 className="font-semibold mb-2">CEFR A1-B2</h4>
              <p className="text-sm text-gray-600">Level pembelajaran sesuai standar internasional</p>
            </div>
            
            <div className="p-4">
              <div className="text-2xl mb-3">📱</div>
              <h4 className="font-semibold mb-2">Mobile-First</h4>
              <p className="text-sm text-gray-600">Akses offline dan pengalaman mobile optimal</p>
            </div>
            
            <div className="p-4">
              <div className="text-2xl mb-3">🔄</div>
              <h4 className="font-semibold mb-2">SRS Algorithm</h4>
              <p className="text-sm text-gray-600">Sistem pengulangan untuk retensi maksimal</p>
            </div>
            
            <div className="p-4">
              <div className="text-2xl mb-3">🏆</div>
              <h4 className="font-semibold mb-2">Gamification</h4>
              <p className="text-sm text-gray-600">Streak, achievement, dan motivasi belajar</p>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}