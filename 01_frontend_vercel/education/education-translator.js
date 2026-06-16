(function () {
  const STORAGE_KEY = 'zenov_lang';
  const DEFAULT_LANG = 'ko-KR';

  const LANGUAGES = {
    'ko-KR': { label: '한국어', html: 'ko', back: '← Zenov 교육자료', ui: { language: '언어', summary: '번역 요약', start: '시작하기 →', next: '다음 →', prev: '← 이전', list: '← 목록', done: '수료하기 →', restart: '↺ 다시 학습하기', original: '한국어 원문으로 표시합니다.' } },
    'en-US': { label: 'English', html: 'en', back: '← Zenov Education', ui: { language: 'Language', summary: 'Translated Summary', start: 'Start →', next: 'Next →', prev: '← Previous', list: '← List', done: 'Complete →', restart: '↺ Restart lesson', original: 'This page uses built-in local English text. No external translation engine is required.' } },
    'th-TH': { label: 'ไทย', html: 'th', back: '← สื่อการเรียนรู้ Zenov', ui: { language: 'ภาษา', summary: 'สรุปฉบับแปล', start: 'เริ่ม →', next: 'ถัดไป →', prev: '← ก่อนหน้า', list: '← รายการ', done: 'จบหลักสูตร →', restart: '↺ เรียนใหม่', original: 'หน้านี้ใช้ข้อความภาษาไทยที่ฝังไว้ในระบบ ไม่ต้องใช้เครื่องมือแปลภายนอก' } },
    'zh-CN': { label: '中文', html: 'zh-CN', back: '← Zenov 教育资料', ui: { language: '语言', summary: '翻译摘要', start: '开始 →', next: '下一步 →', prev: '← 上一步', list: '← 列表', done: '完成 →', restart: '↺ 重新学习', original: '本页使用内置中文文本，无需外部翻译引擎。' } },
    'vi-VN': { label: 'Tiếng Việt', html: 'vi', back: '← Tài liệu đào tạo Zenov', ui: { language: 'Ngôn ngữ', summary: 'Tóm tắt bản dịch', start: 'Bắt đầu →', next: 'Tiếp →', prev: '← Trước', list: '← Danh sách', done: 'Hoàn thành →', restart: '↺ Học lại', original: 'Trang này dùng nội dung tiếng Việt nhúng sẵn, không cần công cụ dịch bên ngoài.' } }
  };

  const COURSE_DATA = {
    'index.html': {
      'ko-KR': {
        title: '탄소중립 교육 플랫폼',
        hero: '같은 탄소중립, 다른 언어로 배웁니다',
        sub: '국민부터 투자사까지 대상별로 다른 관점과 언어로 설계된 6개의 맞춤 교육 과정입니다.',
        bullets: ['국민, 기업, 대기업, IPO, 투자사, 정부기관용 교육을 한곳에서 제공합니다.', '각 교육은 대상자가 실제로 궁금해하는 언어와 사례로 구성됩니다.', 'Zenov 플랫폼 안에서 교육자료를 바로 열고 학습할 수 있습니다.'],
        cards: ['탄소중립, 왜 나와 상관있을까요?', '기업 탄소관리 실무 교육', '대기업 탄소 전략 교육', 'IPO ESG 준비 과정', '탄소시장 투자 분석', '국가 탄소중립 정책 교육']
      },
      'en-US': {
        title: 'Carbon Neutrality Education Platform',
        hero: 'One carbon-neutrality topic, explained in different languages',
        sub: 'Six tailored courses for citizens, companies, enterprises, IPO teams, investors, and government agencies.',
        bullets: ['A single education hub for citizens, companies, enterprises, IPO teams, investors, and public agencies.', 'Each course uses the examples and language that matter to its audience.', 'Education materials can be opened directly inside the Zenov platform.'],
        cards: ['Why does carbon neutrality matter to me?', 'Corporate carbon management practice', 'Enterprise carbon strategy', 'IPO ESG preparation', 'Carbon market investment analysis', 'National carbon policy education']
      },
      'th-TH': {
        title: 'แพลตฟอร์มการเรียนรู้คาร์บอนนิวทรัล',
        hero: 'หัวข้อคาร์บอนนิวทรัลเดียวกัน อธิบายด้วยภาษาที่เหมาะกับแต่ละกลุ่ม',
        sub: 'หลักสูตร 6 แบบสำหรับประชาชน บริษัท องค์กรขนาดใหญ่ ทีม IPO นักลงทุน และหน่วยงานรัฐ',
        bullets: ['รวมหลักสูตรสำหรับประชาชน ธุรกิจ นักลงทุน และภาครัฐไว้ในที่เดียว', 'แต่ละหลักสูตรใช้ตัวอย่างและภาษาที่เหมาะกับผู้เรียน', 'เปิดสื่อการเรียนรู้ได้ทันทีภายในแพลตฟอร์ม Zenov'],
        cards: ['คาร์บอนนิวทรัลเกี่ยวข้องกับฉันอย่างไร?', 'การจัดการคาร์บอนสำหรับองค์กร', 'กลยุทธ์คาร์บอนสำหรับองค์กรขนาดใหญ่', 'การเตรียม ESG สำหรับ IPO', 'การวิเคราะห์การลงทุนในตลาดคาร์บอน', 'นโยบายคาร์บอนนิวทรัลระดับประเทศ']
      },
      'zh-CN': {
        title: '碳中和教育平台',
        hero: '同一个碳中和主题，用不同受众的语言说明',
        sub: '面向公众、企业、大型集团、IPO团队、投资机构和政府部门的六类定制课程。',
        bullets: ['在一个入口提供公众、企业、投资者和政府所需的教育材料。', '每门课程都使用目标受众能理解的案例和语言。', '可在 Zenov 平台内直接打开并学习。'],
        cards: ['碳中和为什么与我有关？', '企业碳管理实务', '大型企业碳战略', 'IPO ESG 准备', '碳市场投资分析', '国家碳中和政策教育']
      },
      'vi-VN': {
        title: 'Nền tảng đào tạo trung hòa carbon',
        hero: 'Cùng một chủ đề carbon, được giải thích bằng ngôn ngữ phù hợp từng nhóm',
        sub: 'Sáu khóa học dành cho công dân, doanh nghiệp, tập đoàn, nhóm IPO, nhà đầu tư và cơ quan nhà nước.',
        bullets: ['Tập hợp tài liệu cho công dân, doanh nghiệp, nhà đầu tư và cơ quan công quyền.', 'Mỗi khóa học dùng ví dụ và ngôn ngữ phù hợp với người học.', 'Có thể mở tài liệu trực tiếp trong nền tảng Zenov.'],
        cards: ['Vì sao trung hòa carbon liên quan đến tôi?', 'Thực hành quản lý carbon doanh nghiệp', 'Chiến lược carbon cho tập đoàn', 'Chuẩn bị ESG cho IPO', 'Phân tích đầu tư thị trường carbon', 'Đào tạo chính sách carbon quốc gia']
      }
    },
    '01_citizen.html': {
      'ko-KR': { title: '탄소중립, 왜 나와 상관있을까요?', hero: '탄소중립, 왜 나와 상관있을까요?', sub: '거창한 환경 이야기가 아닙니다. 오늘 내 밥상, 내 여름, 내 아이의 미래 이야기입니다.', bullets: ['탄소는 생명과 생태계에 필요한 원소입니다.', '문제는 화석연료 사용으로 대기 중 탄소가 과도하게 늘어난 것입니다.', '탄소중립은 배출과 흡수의 균형을 맞추는 실천입니다.'] },
      'en-US': { title: 'Why does carbon neutrality matter to me?', hero: 'Why does carbon neutrality matter to me?', sub: 'This is not a distant environmental topic. It affects food, heat waves, health, and the next generation.', bullets: ['Carbon itself is essential for life and ecosystems.', 'The problem is excessive atmospheric carbon from fossil fuels.', 'Carbon neutrality means balancing emissions with removal and storage.'] },
      'th-TH': { title: 'คาร์บอนนิวทรัลเกี่ยวข้องกับฉันอย่างไร?', hero: 'คาร์บอนนิวทรัลเกี่ยวข้องกับฉันอย่างไร?', sub: 'ไม่ใช่เรื่องสิ่งแวดล้อมที่ไกลตัว แต่เกี่ยวกับอาหาร อากาศ สุขภาพ และอนาคตของลูกหลาน', bullets: ['คาร์บอนเป็นองค์ประกอบสำคัญของชีวิตและระบบนิเวศ', 'ปัญหาคือการปล่อยคาร์บอนจากเชื้อเพลิงฟอสซิลมากเกินไป', 'คาร์บอนนิวทรัลคือการทำให้การปล่อยและการดูดซับสมดุลกัน'] },
      'zh-CN': { title: '碳中和为什么与我有关？', hero: '碳中和为什么与我有关？', sub: '这不是遥远的环保话题，而是关系到食物、夏天、健康和下一代的现实问题。', bullets: ['碳本身是生命和生态系统必需的元素。', '问题在于化石燃料导致大气中过量碳累积。', '碳中和是让排放与吸收、储存达到平衡。'] },
      'vi-VN': { title: 'Vì sao trung hòa carbon liên quan đến tôi?', hero: 'Vì sao trung hòa carbon liên quan đến tôi?', sub: 'Đây không phải chuyện môi trường xa vời, mà liên quan đến bữa ăn, mùa hè, sức khỏe và tương lai con em chúng ta.', bullets: ['Carbon là thành phần cần thiết cho sự sống và hệ sinh thái.', 'Vấn đề là carbon trong khí quyển tăng quá mức do nhiên liệu hóa thạch.', 'Trung hòa carbon là cân bằng giữa phát thải và hấp thụ/lưu trữ.'] }
    },
    '02_corporate.html': {
      'ko-KR': { title: '기업 탄소관리 실무 교육', hero: '탄소는 이제 기업 경쟁력 문제입니다', sub: 'ESG 공시, Scope 배출량, 공급망 탄소관리까지 실무자가 알아야 할 핵심을 정리했습니다.', bullets: ['탄소 데이터는 수출, 입찰, 투자유치에 직접 영향을 줍니다.', 'Scope 1, 2, 3 배출량을 이해해야 ESG 대응이 가능합니다.', 'MRV와 데이터 신뢰성이 그린워싱 리스크를 줄입니다.'] },
      'en-US': { title: 'Corporate Carbon Management Practice', hero: 'Carbon is now a business competitiveness issue', sub: 'A practical guide to ESG disclosure, Scope emissions, supply-chain carbon data, and MRV.', bullets: ['Carbon data affects exports, tenders, and investment decisions.', 'Companies need Scope 1, 2, and 3 literacy for ESG readiness.', 'MRV and trusted data reduce greenwashing risk.'] },
      'th-TH': { title: 'การจัดการคาร์บอนสำหรับองค์กร', hero: 'คาร์บอนคือปัจจัยความสามารถในการแข่งขันของธุรกิจ', sub: 'คู่มือปฏิบัติเรื่อง ESG, Scope emissions, ห่วงโซ่อุปทาน และ MRV', bullets: ['ข้อมูลคาร์บอนมีผลต่อการส่งออก การประมูล และการลงทุน', 'ต้องเข้าใจ Scope 1, 2, 3 เพื่อรับมือ ESG', 'MRV และข้อมูลที่เชื่อถือได้ช่วยลดความเสี่ยง greenwashing'] },
      'zh-CN': { title: '企业碳管理实务', hero: '碳管理已经成为企业竞争力问题', sub: '涵盖 ESG 披露、Scope 排放、供应链碳管理和 MRV 的实务指南。', bullets: ['碳数据会影响出口、投标和融资。', '企业必须理解 Scope 1、2、3 才能应对 ESG。', 'MRV 和可信数据可以降低漂绿风险。'] },
      'vi-VN': { title: 'Thực hành quản lý carbon doanh nghiệp', hero: 'Carbon đã trở thành vấn đề năng lực cạnh tranh', sub: 'Hướng dẫn thực tế về công bố ESG, phát thải Scope, chuỗi cung ứng và MRV.', bullets: ['Dữ liệu carbon ảnh hưởng đến xuất khẩu, đấu thầu và gọi vốn.', 'Doanh nghiệp cần hiểu Scope 1, 2, 3 để sẵn sàng ESG.', 'MRV và dữ liệu đáng tin cậy giúp giảm rủi ro greenwashing.'] }
    },
    '03_enterprise.html': {
      'ko-KR': { title: '대기업 탄소 전략 교육', hero: '탄소는 비용이 아니라 전략입니다', sub: '글로벌 규제, 공급망 리스크, 탄소 데이터 통합을 기업 전략 관점에서 설명합니다.', bullets: ['대기업은 공급망 전체의 탄소 리스크를 관리해야 합니다.', '탄소 데이터 통합은 규제 대응과 브랜드 가치에 영향을 줍니다.', 'AI MRV는 글로벌 탄소 전략의 운영 인프라가 됩니다.'] },
      'en-US': { title: 'Enterprise Carbon Strategy', hero: 'Carbon is not only a cost. It is strategy.', sub: 'A strategy view of global regulation, supply-chain risk, and integrated carbon data.', bullets: ['Enterprises must manage carbon risk across the full supply chain.', 'Integrated carbon data affects compliance and brand value.', 'AI MRV becomes the operating infrastructure for carbon strategy.'] },
      'th-TH': { title: 'กลยุทธ์คาร์บอนสำหรับองค์กรขนาดใหญ่', hero: 'คาร์บอนไม่ใช่แค่ต้นทุน แต่คือกลยุทธ์', sub: 'มุมมองเชิงกลยุทธ์ต่อกฎระเบียบโลก ความเสี่ยงห่วงโซ่อุปทาน และข้อมูลคาร์บอน', bullets: ['องค์กรขนาดใหญ่ต้องบริหารความเสี่ยงคาร์บอนทั้งห่วงโซ่อุปทาน', 'ข้อมูลคาร์บอนแบบรวมศูนย์มีผลต่อ compliance และแบรนด์', 'AI MRV เป็นโครงสร้างพื้นฐานของกลยุทธ์คาร์บอน'] },
      'zh-CN': { title: '大型企业碳战略', hero: '碳不只是成本，而是战略', sub: '从全球监管、供应链风险和碳数据整合角度解释企业战略。', bullets: ['大型企业必须管理整个供应链的碳风险。', '碳数据整合影响合规和品牌价值。', 'AI MRV 将成为碳战略的运营基础设施。'] },
      'vi-VN': { title: 'Chiến lược carbon cho tập đoàn', hero: 'Carbon không chỉ là chi phí, mà là chiến lược', sub: 'Góc nhìn chiến lược về quy định toàn cầu, rủi ro chuỗi cung ứng và dữ liệu carbon tích hợp.', bullets: ['Tập đoàn phải quản lý rủi ro carbon trên toàn chuỗi cung ứng.', 'Dữ liệu carbon tích hợp ảnh hưởng đến tuân thủ và giá trị thương hiệu.', 'AI MRV là hạ tầng vận hành cho chiến lược carbon.'] }
    },
    '04_ipo.html': {
      'ko-KR': { title: 'IPO ESG 준비 과정', hero: 'ESG 데이터가 기업가치를 결정합니다', sub: '상장 전 투자자가 요구하는 ESG 데이터, 공시, 신뢰성 준비 항목을 정리했습니다.', bullets: ['투자자는 ESG 데이터로 미래 리스크를 평가합니다.', '탄소 데이터의 정확성과 추적성이 기업가치에 연결됩니다.', '상장 전 MRV와 감사 가능한 데이터 체계를 준비해야 합니다.'] },
      'en-US': { title: 'IPO ESG Preparation', hero: 'ESG data shapes enterprise value', sub: 'What IPO-ready companies need for ESG data, disclosure, and trust.', bullets: ['Investors use ESG data to evaluate future risk.', 'Accuracy and traceability of carbon data affect valuation.', 'MRV and auditable data systems should be ready before listing.'] },
      'th-TH': { title: 'การเตรียม ESG สำหรับ IPO', hero: 'ข้อมูล ESG กำหนดมูลค่าบริษัท', sub: 'สิ่งที่บริษัทก่อน IPO ต้องเตรียมด้านข้อมูล ESG การเปิดเผย และความน่าเชื่อถือ', bullets: ['นักลงทุนใช้ข้อมูล ESG เพื่อประเมินความเสี่ยงอนาคต', 'ความถูกต้องและการติดตามข้อมูลคาร์บอนมีผลต่อมูลค่า', 'ควรเตรียม MRV และระบบข้อมูลที่ตรวจสอบได้ก่อนเข้าตลาด'] },
      'zh-CN': { title: 'IPO ESG 准备', hero: 'ESG 数据决定企业价值', sub: '上市前企业需要准备的 ESG 数据、披露和可信度要求。', bullets: ['投资者用 ESG 数据评估未来风险。', '碳数据的准确性和可追溯性影响估值。', '上市前应建立 MRV 和可审计的数据体系。'] },
      'vi-VN': { title: 'Chuẩn bị ESG cho IPO', hero: 'Dữ liệu ESG quyết định giá trị doanh nghiệp', sub: 'Những yêu cầu về dữ liệu ESG, công bố và độ tin cậy trước khi niêm yết.', bullets: ['Nhà đầu tư dùng dữ liệu ESG để đánh giá rủi ro tương lai.', 'Độ chính xác và khả năng truy xuất dữ liệu carbon ảnh hưởng đến định giá.', 'Cần chuẩn bị MRV và hệ thống dữ liệu có thể kiểm toán trước IPO.'] }
    },
    '05_investor.html': {
      'ko-KR': { title: '탄소시장 투자 분석', hero: '탄소는 새로운 자산 시장입니다', sub: '탄소 크레딧, MRV 플랫폼, AI 감축 기술을 투자 관점에서 분석합니다.', bullets: ['탄소시장은 규제시장과 자발적 시장으로 나뉩니다.', '크레딧 가치는 신뢰도, 방법론, 검증 수준에 따라 달라집니다.', 'AI MRV 플랫폼은 탄소 자산 시장의 인프라가 될 수 있습니다.'] },
      'en-US': { title: 'Carbon Market Investment Analysis', hero: 'Carbon is a new asset market', sub: 'An investor view of carbon credits, MRV platforms, and AI reduction technologies.', bullets: ['Carbon markets include compliance markets and voluntary markets.', 'Credit value depends on trust, methodology, and verification quality.', 'AI MRV platforms can become infrastructure for carbon asset markets.'] },
      'th-TH': { title: 'การวิเคราะห์การลงทุนในตลาดคาร์บอน', hero: 'คาร์บอนคือสินทรัพย์ตลาดใหม่', sub: 'มุมมองนักลงทุนต่อ carbon credits, MRV platform และเทคโนโลยี AI ลดคาร์บอน', bullets: ['ตลาดคาร์บอนแบ่งเป็นตลาดกำกับและตลาดสมัครใจ', 'มูลค่าเครดิตขึ้นกับความน่าเชื่อถือ วิธีวิทยา และการตรวจสอบ', 'AI MRV อาจเป็นโครงสร้างพื้นฐานของตลาดสินทรัพย์คาร์บอน'] },
      'zh-CN': { title: '碳市场投资分析', hero: '碳是新的资产市场', sub: '从投资角度分析碳信用、MRV 平台和 AI 减排技术。', bullets: ['碳市场包括合规市场和自愿市场。', '信用价值取决于信任、方法学和验证质量。', 'AI MRV 平台可能成为碳资产市场基础设施。'] },
      'vi-VN': { title: 'Phân tích đầu tư thị trường carbon', hero: 'Carbon là một thị trường tài sản mới', sub: 'Góc nhìn đầu tư về tín chỉ carbon, nền tảng MRV và công nghệ AI giảm phát thải.', bullets: ['Thị trường carbon gồm thị trường bắt buộc và tự nguyện.', 'Giá trị tín chỉ phụ thuộc vào độ tin cậy, phương pháp luận và xác minh.', 'Nền tảng AI MRV có thể trở thành hạ tầng của thị trường tài sản carbon.'] }
    },
    '06_government.html': {
      'ko-KR': { title: '국가 탄소중립 정책 교육', hero: '탄소중립은 국가 산업 전략입니다', sub: '탄소 데이터와 AI 기반 MRV를 국가 경쟁력 인프라 관점에서 설명합니다.', bullets: ['탄소중립은 환경정책을 넘어 산업정책입니다.', '국가 MRV 체계는 감축 성과를 증명하는 핵심 인프라입니다.', '민간 자본과 검증 데이터가 결합되어 탄소 산업 생태계가 만들어집니다.'] },
      'en-US': { title: 'National Carbon Policy Education', hero: 'Carbon neutrality is national industrial strategy', sub: 'Carbon data and AI MRV as infrastructure for national competitiveness.', bullets: ['Carbon neutrality is industrial policy, not only environmental policy.', 'A national MRV system proves reduction performance.', 'Private capital and verified data can build a carbon industry ecosystem.'] },
      'th-TH': { title: 'นโยบายคาร์บอนนิวทรัลระดับประเทศ', hero: 'คาร์บอนนิวทรัลคือยุทธศาสตร์อุตสาหกรรมของประเทศ', sub: 'ข้อมูลคาร์บอนและ AI MRV ในฐานะโครงสร้างพื้นฐานความสามารถแข่งขันของประเทศ', bullets: ['คาร์บอนนิวทรัลเป็นนโยบายอุตสาหกรรม ไม่ใช่แค่นโยบายสิ่งแวดล้อม', 'ระบบ MRV ระดับชาติพิสูจน์ผลการลดคาร์บอน', 'เงินทุนเอกชนและข้อมูลที่ตรวจสอบแล้วสร้างระบบนิเวศอุตสาหกรรมคาร์บอน'] },
      'zh-CN': { title: '国家碳中和政策教育', hero: '碳中和是国家产业战略', sub: '从国家竞争力基础设施角度解释碳数据和 AI MRV。', bullets: ['碳中和不只是环境政策，也是产业政策。', '国家 MRV 体系是证明减排成果的关键基础设施。', '民间资本与可信数据结合可形成碳产业生态。'] },
      'vi-VN': { title: 'Đào tạo chính sách carbon quốc gia', hero: 'Trung hòa carbon là chiến lược công nghiệp quốc gia', sub: 'Dữ liệu carbon và AI MRV như hạ tầng cho năng lực cạnh tranh quốc gia.', bullets: ['Trung hòa carbon là chính sách công nghiệp, không chỉ là môi trường.', 'Hệ thống MRV quốc gia chứng minh kết quả giảm phát thải.', 'Vốn tư nhân và dữ liệu đã xác minh tạo nên hệ sinh thái công nghiệp carbon.'] }
    }
  };

  const FULL_COURSE_DATA = {
    '01_citizen.html': {
      'en-US': {
        kicker: 'Citizen Course',
        title: 'Why does carbon neutrality matter to me?',
        sub: 'Carbon neutrality is not a distant environmental slogan. It is connected to food prices, summer heat, floods, health, jobs, and the future of the next generation.',
        chapters: [
          {
            title: '1. Carbon itself is not bad',
            body: 'Carbon is a basic element of life. Plants, animals, soil, oceans, and the atmosphere all exchange carbon through the natural carbon cycle. The problem is not carbon itself; the problem is too much carbon accumulating in the atmosphere.',
            cards: [
              ['Atmosphere', 'CO₂ exists naturally in the air and helps keep Earth warm enough for life.'],
              ['Plants', 'Plants absorb CO₂ through photosynthesis and store carbon in leaves, roots, and trunks.'],
              ['Soil and oceans', 'Soil and oceans store massive amounts of carbon and help stabilize the climate.'],
              ['Fossil fuels', 'Coal, oil, and gas are carbon stored underground for millions of years.']
            ],
            quiz: 'Key point: carbon is essential, but the balance is broken when too much stored fossil carbon is released quickly.'
          },
          {
            title: '2. Why did it become a problem now?',
            body: 'For about 200 years, humans have burned coal, oil, and gas at industrial scale. This released carbon that had been stored underground for millions of years. Nature cannot absorb it as quickly as we emit it.',
            cards: [
              ['Industry', 'Factories, power plants, transport, buildings, and agriculture all add emissions.'],
              ['Speed', 'The natural carbon cycle is slow, but human emissions are extremely fast.'],
              ['Concentration', 'More CO₂ in the atmosphere strengthens the greenhouse effect.'],
              ['Result', 'Average temperature rises and extreme weather becomes more frequent.']
            ],
            quiz: 'Key point: climate change is caused by the speed and scale of fossil-fuel emissions.'
          },
          {
            title: '3. How climate change affects daily life',
            body: 'Climate change appears in daily life as heat waves, heavy rain, flooding, drought, crop damage, higher food prices, health risks, and rising insurance and energy costs.',
            cards: [
              ['Food', 'Heat and drought reduce crop yields and raise food prices.'],
              ['Health', 'Heat waves increase heat illness, respiratory stress, and risks for vulnerable people.'],
              ['Homes and cities', 'Floods and storms damage infrastructure and increase public costs.'],
              ['Economy', 'Energy bills, insurance, logistics, and supply chains all become more unstable.']
            ],
            quiz: 'Key point: carbon emissions are connected to household costs, safety, and health.'
          },
          {
            title: '4. What carbon neutrality means',
            body: 'Carbon neutrality does not mean removing all carbon from Earth. It means balancing emissions with absorption, removal, or storage so that net emissions become zero.',
            cards: [
              ['Reduce', 'Use less fossil energy through efficiency, renewable energy, and cleaner transport.'],
              ['Replace', 'Switch from fossil-fuel systems to electric, solar, wind, and low-carbon alternatives.'],
              ['Remove', 'Protect forests, restore ecosystems, and use verified carbon removal where appropriate.'],
              ['Measure', 'Reliable data and MRV are needed to prove real reductions.']
            ],
            quiz: 'Key point: Net Zero means emissions and removals are balanced with reliable proof.'
          },
          {
            title: '5. What I can do today',
            body: 'Individual action matters when millions of people act together. The most practical actions are reducing waste, saving energy, choosing public transport or EV mobility, eating lower-carbon meals, and supporting verified climate projects.',
            cards: [
              ['Transport', 'Use public transport, walking, cycling, or shared mobility when possible.'],
              ['Energy', 'Reduce electricity waste and support renewable power.'],
              ['Food and waste', 'Reduce food waste and choose lower-carbon meals more often.'],
              ['Data', 'Support projects that measure, verify, and report real reductions.']
            ],
            quiz: 'Key point: the easiest action is to start with daily choices and support verified climate data.'
          }
        ],
        finalTitle: 'You completed the citizen carbon-neutrality course',
        finalBullets: [
          'Carbon is not the enemy; excess atmospheric carbon is the problem.',
          'Fossil fuels released stored carbon too quickly.',
          'Climate change directly affects food, health, safety, and costs.',
          'Carbon neutrality means balancing emissions with verified reduction and removal.',
          'Everyday choices and trusted MRV data both matter.'
        ]
      },
      'th-TH': {
        kicker: 'หลักสูตรสำหรับประชาชน',
        title: 'คาร์บอนนิวทรัลเกี่ยวข้องกับฉันอย่างไร?',
        sub: 'คาร์บอนนิวทรัลไม่ใช่คำขวัญด้านสิ่งแวดล้อมที่ไกลตัว แต่เกี่ยวข้องกับราคาอาหาร ความร้อน น้ำท่วม สุขภาพ งาน และอนาคตของลูกหลาน',
        chapters: [
          { title: '1. คาร์บอนไม่ใช่สิ่งเลวร้ายโดยตัวมันเอง', body: 'คาร์บอนเป็นองค์ประกอบพื้นฐานของชีวิต พืช สัตว์ ดิน มหาสมุทร และบรรยากาศแลกเปลี่ยนคาร์บอนผ่านวัฏจักรธรรมชาติ ปัญหาไม่ใช่คาร์บอน แต่คือคาร์บอนในชั้นบรรยากาศที่มากเกินไป', cards: [['บรรยากาศ','CO₂ มีอยู่ตามธรรมชาติและช่วยให้โลกอบอุ่นพอสำหรับชีวิต'],['พืช','พืชดูดซับ CO₂ ผ่านการสังเคราะห์แสงและเก็บคาร์บอนไว้'],['ดินและทะเล','ดินและทะเลเป็นแหล่งกักเก็บคาร์บอนขนาดใหญ่'],['เชื้อเพลิงฟอสซิล','ถ่านหิน น้ำมัน และก๊าซคือคาร์บอนที่ถูกเก็บใต้ดินมาหลายล้านปี']], quiz: 'ประเด็นสำคัญ: คาร์บอนจำเป็นต่อชีวิต แต่สมดุลเสียเมื่อปล่อยคาร์บอนฟอสซิลเร็วเกินไป' },
          { title: '2. ทำไมจึงกลายเป็นปัญหาตอนนี้?', body: 'ในช่วงประมาณ 200 ปี มนุษย์เผาถ่านหิน น้ำมัน และก๊าซในระดับอุตสาหกรรม ทำให้คาร์บอนที่ถูกเก็บมาหลายล้านปีถูกปล่อยออกมาอย่างรวดเร็ว ธรรมชาติไม่สามารถดูดซับได้ทัน', cards: [['อุตสาหกรรม','โรงงาน ไฟฟ้า ขนส่ง อาคาร และเกษตรเพิ่มการปล่อย'],['ความเร็ว','วัฏจักรธรรมชาติช้า แต่การปล่อยของมนุษย์เร็วมาก'],['ความเข้มข้น','CO₂ ที่มากขึ้นทำให้ภาวะเรือนกระจกแรงขึ้น'],['ผลลัพธ์','อุณหภูมิเฉลี่ยสูงขึ้นและอากาศสุดขั้วบ่อยขึ้น']], quiz: 'ประเด็นสำคัญ: ปัญหามาจากความเร็วและขนาดของการปล่อยจากเชื้อเพลิงฟอสซิล' },
          { title: '3. ผลกระทบต่อชีวิตประจำวัน', body: 'การเปลี่ยนแปลงสภาพภูมิอากาศปรากฏเป็นคลื่นความร้อน ฝนหนัก น้ำท่วม ภัยแล้ง ผลผลิตเสียหาย ราคาอาหารสูงขึ้น ความเสี่ยงสุขภาพ และต้นทุนพลังงาน/ประกันภัยที่เพิ่มขึ้น', cards: [['อาหาร','ความร้อนและภัยแล้งทำให้ผลผลิตลดลงและราคาอาหารสูงขึ้น'],['สุขภาพ','คลื่นความร้อนเพิ่มความเสี่ยงต่อโรคลมร้อนและระบบหายใจ'],['บ้านและเมือง','น้ำท่วมและพายุทำลายโครงสร้างพื้นฐาน'],['เศรษฐกิจ','ค่าไฟ ประกัน โลจิสติกส์ และห่วงโซ่อุปทานผันผวนมากขึ้น']], quiz: 'ประเด็นสำคัญ: การปล่อยคาร์บอนเชื่อมโยงกับค่าใช้จ่าย ความปลอดภัย และสุขภาพ' },
          { title: '4. ความหมายของคาร์บอนนิวทรัล', body: 'คาร์บอนนิวทรัลไม่ได้หมายถึงการกำจัดคาร์บอนทั้งหมด แต่หมายถึงการทำให้การปล่อยสมดุลกับการดูดซับ การกำจัด หรือการกักเก็บ จนการปล่อยสุทธิเป็นศูนย์', cards: [['ลด','ใช้พลังงานฟอสซิลให้น้อยลง'],['เปลี่ยน','เปลี่ยนเป็นไฟฟ้า พลังงานแสงอาทิตย์ ลม และระบบคาร์บอนต่ำ'],['ดูดซับ','ปกป้องป่า ฟื้นฟูระบบนิเวศ และใช้การกำจัดคาร์บอนที่ตรวจสอบได้'],['วัดผล','ต้องมีข้อมูลและ MRV ที่เชื่อถือได้']], quiz: 'ประเด็นสำคัญ: Net Zero ต้องมีทั้งการลดและหลักฐานที่น่าเชื่อถือ' },
          { title: '5. สิ่งที่ทำได้วันนี้', body: 'การกระทำของคนหนึ่งคนมีความหมายเมื่อหลายล้านคนทำร่วมกัน เริ่มได้จากลดขยะ ประหยัดพลังงาน ใช้ขนส่งสาธารณะหรือ EV เลือกอาหารคาร์บอนต่ำ และสนับสนุนโครงการที่ตรวจสอบได้', cards: [['การเดินทาง','ใช้ขนส่งสาธารณะ เดิน จักรยาน หรือแชร์รถ'],['พลังงาน','ลดการใช้ไฟฟ้าสิ้นเปลืองและสนับสนุนพลังงานหมุนเวียน'],['อาหารและขยะ','ลดขยะอาหารและเลือกอาหารคาร์บอนต่ำมากขึ้น'],['ข้อมูล','สนับสนุนโครงการที่วัด ตรวจสอบ และรายงานผลจริง']], quiz: 'ประเด็นสำคัญ: เริ่มจากชีวิตประจำวันและสนับสนุนข้อมูล MRV ที่น่าเชื่อถือ' }
        ],
        finalTitle: 'คุณเรียนจบหลักสูตรคาร์บอนนิวทรัลสำหรับประชาชนแล้ว',
        finalBullets: ['คาร์บอนไม่ใช่ศัตรู ปัญหาคือคาร์บอนในบรรยากาศมากเกินไป','เชื้อเพลิงฟอสซิลปล่อยคาร์บอนที่สะสมไว้อย่างรวดเร็ว','ภูมิอากาศกระทบอาหาร สุขภาพ ความปลอดภัย และต้นทุน','คาร์บอนนิวทรัลคือสมดุลด้วยการลดและการพิสูจน์','การเลือกในชีวิตประจำวันและข้อมูล MRV ที่เชื่อถือได้สำคัญทั้งคู่']
      },
      'vi-VN': {
        kicker: 'Khóa học cho công dân',
        title: 'Vì sao trung hòa carbon liên quan đến tôi?',
        sub: 'Trung hòa carbon không phải khẩu hiệu môi trường xa vời. Nó liên quan đến giá thực phẩm, nắng nóng, lũ lụt, sức khỏe, việc làm và tương lai thế hệ sau.',
        chapters: [
          { title: '1. Carbon không xấu tự thân', body: 'Carbon là thành phần cơ bản của sự sống. Cây cối, động vật, đất, đại dương và khí quyển trao đổi carbon qua chu trình tự nhiên. Vấn đề không phải là carbon, mà là quá nhiều carbon tích tụ trong khí quyển.', cards: [['Khí quyển','CO₂ tồn tại tự nhiên và giúp Trái Đất đủ ấm cho sự sống'],['Thực vật','Cây hấp thụ CO₂ qua quang hợp và lưu trữ carbon'],['Đất và đại dương','Đây là các kho lưu trữ carbon khổng lồ'],['Nhiên liệu hóa thạch','Than, dầu và khí là carbon được lưu giữ dưới đất hàng triệu năm']], quiz: 'Điểm chính: carbon cần thiết, nhưng cân bằng bị phá vỡ khi carbon hóa thạch được thải quá nhanh.' },
          { title: '2. Vì sao bây giờ thành vấn đề?', body: 'Trong khoảng 200 năm, con người đã đốt than, dầu và khí ở quy mô công nghiệp. Lượng carbon được lưu giữ hàng triệu năm bị thải ra quá nhanh, vượt khả năng hấp thụ của tự nhiên.', cards: [['Công nghiệp','Nhà máy, điện, giao thông, tòa nhà và nông nghiệp đều phát thải'],['Tốc độ','Chu trình tự nhiên chậm, phát thải của con người rất nhanh'],['Nồng độ','CO₂ tăng làm hiệu ứng nhà kính mạnh hơn'],['Kết quả','Nhiệt độ tăng và thời tiết cực đoan thường xuyên hơn']], quiz: 'Điểm chính: nguyên nhân là tốc độ và quy mô phát thải từ nhiên liệu hóa thạch.' },
          { title: '3. Ảnh hưởng đến đời sống', body: 'Biến đổi khí hậu thể hiện qua nắng nóng, mưa lớn, lũ lụt, hạn hán, thiệt hại mùa màng, giá thực phẩm tăng, rủi ro sức khỏe và chi phí năng lượng/bảo hiểm cao hơn.', cards: [['Thực phẩm','Nắng nóng và hạn hán làm giảm năng suất và tăng giá'],['Sức khỏe','Nắng nóng làm tăng bệnh do nhiệt và vấn đề hô hấp'],['Nhà cửa và đô thị','Lũ lụt và bão gây hư hại hạ tầng'],['Kinh tế','Điện, bảo hiểm, logistics và chuỗi cung ứng bất ổn hơn']], quiz: 'Điểm chính: phát thải carbon liên quan trực tiếp đến chi phí, an toàn và sức khỏe.' },
          { title: '4. Trung hòa carbon là gì?', body: 'Trung hòa carbon không có nghĩa là xóa bỏ mọi carbon. Nó là cân bằng phát thải với hấp thụ, loại bỏ hoặc lưu trữ để phát thải ròng bằng 0.', cards: [['Giảm','Dùng ít năng lượng hóa thạch hơn'],['Thay thế','Chuyển sang điện, mặt trời, gió và hệ thống carbon thấp'],['Loại bỏ','Bảo vệ rừng, phục hồi hệ sinh thái và loại bỏ carbon có xác minh'],['Đo lường','Cần dữ liệu và MRV đáng tin cậy']], quiz: 'Điểm chính: Net Zero cần giảm phát thải và bằng chứng đáng tin cậy.' },
          { title: '5. Tôi có thể làm gì hôm nay?', body: 'Hành động cá nhân có ý nghĩa khi nhiều người cùng làm. Hãy giảm lãng phí, tiết kiệm năng lượng, dùng giao thông công cộng/EV, ăn ít carbon hơn và ủng hộ dự án khí hậu được xác minh.', cards: [['Giao thông','Dùng xe công cộng, đi bộ, xe đạp hoặc di chuyển chia sẻ'],['Năng lượng','Giảm lãng phí điện và ủng hộ năng lượng tái tạo'],['Thực phẩm và rác','Giảm lãng phí thực phẩm và chọn bữa ăn ít carbon'],['Dữ liệu','Ủng hộ dự án đo, xác minh và báo cáo kết quả thật']], quiz: 'Điểm chính: bắt đầu từ lựa chọn hằng ngày và dữ liệu MRV đáng tin cậy.' }
        ],
        finalTitle: 'Bạn đã hoàn thành khóa học công dân về trung hòa carbon',
        finalBullets: ['Carbon không phải kẻ thù; carbon dư thừa trong khí quyển mới là vấn đề.','Nhiên liệu hóa thạch thải carbon lưu trữ quá nhanh.','Khí hậu ảnh hưởng trực tiếp đến thực phẩm, sức khỏe, an toàn và chi phí.','Trung hòa carbon là cân bằng bằng giảm phát thải và bằng chứng xác minh.','Lựa chọn hằng ngày và dữ liệu MRV đáng tin cậy đều quan trọng.']
      },
      'zh-CN': {
        kicker: '公众课程',
        title: '碳中和为什么与我有关？',
        sub: '碳中和不是遥远的环保口号，它关系到食品价格、夏季高温、洪水、健康、就业和下一代的未来。',
        chapters: [
          { title: '1. 碳本身并不坏', body: '碳是生命的基本元素。植物、动物、土壤、海洋和大气通过自然碳循环交换碳。问题不是碳本身，而是过量碳在大气中累积。', cards: [['大气','CO₂ 自然存在，并让地球保持适合生命的温度'],['植物','植物通过光合作用吸收 CO₂ 并储存碳'],['土壤和海洋','它们是巨大的碳储存库'],['化石燃料','煤、石油和天然气是地下储存了数百万年的碳']], quiz: '重点：碳是必需的，但当化石碳被快速释放时，平衡就被打破。' },
          { title: '2. 为什么现在成了问题？', body: '过去约 200 年，人类大规模燃烧煤、石油和天然气。数百万年储存的碳被快速释放，自然无法同速吸收。', cards: [['工业','工厂、电力、交通、建筑和农业都会增加排放'],['速度','自然碳循环很慢，人类排放却很快'],['浓度','更多 CO₂ 会增强温室效应'],['结果','平均气温上升，极端天气更频繁']], quiz: '重点：问题来自化石燃料排放的速度和规模。' },
          { title: '3. 对日常生活的影响', body: '气候变化表现为热浪、暴雨、洪水、干旱、农作物受损、食品价格上涨、健康风险以及能源和保险成本上升。', cards: [['食物','高温和干旱降低产量并推高价格'],['健康','热浪增加中暑和呼吸系统风险'],['住房和城市','洪水和风暴破坏基础设施'],['经济','电费、保险、物流和供应链更不稳定']], quiz: '重点：碳排放与家庭成本、安全和健康直接相关。' },
          { title: '4. 什么是碳中和？', body: '碳中和不是消灭地球上所有碳，而是让排放与吸收、清除或储存达到平衡，使净排放为零。', cards: [['减少','通过效率和清洁能源减少化石能源使用'],['替代','从化石系统转向电动、太阳能、风能和低碳方案'],['清除','保护森林、恢复生态并使用可验证的碳清除'],['测量','需要可靠数据和 MRV 来证明真实减排']], quiz: '重点：净零意味着排放和清除达到平衡，并有可信证据。' },
          { title: '5. 今天我能做什么？', body: '当很多人一起行动时，个人选择就有力量。可以从减少浪费、节能、公共交通或电动出行、低碳饮食，以及支持可验证的气候项目开始。', cards: [['交通','尽量使用公共交通、步行、骑行或共享出行'],['能源','减少用电浪费并支持可再生能源'],['食物和垃圾','减少食物浪费，更多选择低碳饮食'],['数据','支持能测量、验证和报告真实减排的项目']], quiz: '重点：从日常选择开始，也要支持可信的 MRV 数据。' }
        ],
        finalTitle: '你已完成公众碳中和课程',
        finalBullets: ['碳不是敌人，过量大气碳才是问题。','化石燃料过快释放了储存碳。','气候变化直接影响食物、健康、安全和成本。','碳中和意味着用减排和可信证据实现平衡。','日常选择和可信 MRV 数据同样重要。']
      }
    },
    '02_corporate.html': {
      'en-US': {
        kicker: 'Corporate Practice Course',
        title: 'Corporate Carbon Management Practice',
        sub: 'Carbon is no longer only an environmental topic. For companies, it is now connected to exports, tenders, finance, supply-chain trust, and business continuity.',
        chapters: [
          { title: '1. Why companies must manage carbon now', body: 'Global customers, investors, and regulators increasingly ask companies to prove their carbon data. Without reliable data, a company may lose export opportunities, supplier status, public procurement points, or financing advantages.', cards: [['Business risk','Carbon data now affects sales, procurement, loans, and investor due diligence.'],['CBAM and trade','Exporters may face additional carbon costs when selling carbon-intensive products into regulated markets.'],['Supply-chain demand','Large customers ask suppliers for emissions data to manage Scope 3.'],['Practical rule','Treat carbon data like financial data: measured, reviewed, and traceable.']], quiz: 'Key point: carbon management is now a business competitiveness issue, not only an ESG slogan.' },
          { title: '2. What ESG means in practice', body: 'ESG means Environment, Social, and Governance. For operating teams, ESG is not a poster or marketing phrase. It is a management system that proves how the company handles environmental data, labor and safety, compliance, and decision-making.', cards: [['Environment','Energy use, emissions, waste, water, and reduction plans.'],['Social','Safety, labor, suppliers, communities, and customer responsibility.'],['Governance','Board oversight, ethics, internal control, and audit trail.'],['Carbon link','Carbon data is one of the most measurable parts of ESG.']], quiz: 'Key point: ESG becomes credible only when it is supported by data and evidence.' },
          { title: '3. Scope 1, 2, and 3 emissions', body: 'Corporate emissions are grouped into Scope 1, Scope 2, and Scope 3. This structure helps companies identify where emissions occur and what data must be collected.', cards: [['Scope 1','Direct emissions from company-owned fuel, vehicles, boilers, or processes.'],['Scope 2','Indirect emissions from purchased electricity, steam, heating, or cooling.'],['Scope 3','Value-chain emissions from suppliers, logistics, business travel, product use, and disposal.'],['First action','Start with data that is available: fuel, electricity, vehicles, and major suppliers.']], quiz: 'Key point: Scope 3 is often the largest and hardest part, so supplier data management matters.' },
          { title: '4. MRV: Measurement, Reporting, Verification', body: 'MRV is the operating discipline for trusted carbon data. Measurement collects the data, Reporting organizes it into a usable format, and Verification checks whether it is reliable.', cards: [['Measurement','Collect energy, mobility, production, sensor, and activity data.'],['Reporting','Convert data into emissions, reductions, and business indicators.'],['Verification','Check hash, source, method, calculation, and audit history.'],['Business value','Verified data reduces greenwashing risk and supports ESG disclosure.']], quiz: 'Key point: MRV turns raw operational data into trusted evidence.' },
          { title: '5. Supply-chain carbon management', body: 'Many companies are asked by customers to submit carbon data because customers must report their own Scope 3 emissions. This means suppliers that can provide reliable data become more competitive.', cards: [['Supplier request','Customers may ask for energy, fuel, logistics, and product carbon data.'],['Data template','Use a consistent questionnaire and data dictionary.'],['Evidence','Keep invoices, meter readings, API logs, and calculation versions.'],['Opportunity','Good carbon data can become a sales advantage.']], quiz: 'Key point: carbon data can help keep existing customers and win new ones.' },
          { title: '6. What to do first', body: 'A company does not need to solve everything on day one. The practical first step is to build a repeatable data flow and assign clear ownership.', cards: [['Step 1','List emission sources: fuel, electricity, vehicles, factory, logistics, suppliers.'],['Step 2','Decide owners for each data source.'],['Step 3','Collect monthly data and store evidence.'],['Step 4','Calculate emissions and reductions with versioned factors.'],['Step 5','Review results and prepare reports for customers, auditors, and executives.']], quiz: 'Key point: begin with a simple monthly MRV routine, then expand.' }
        ],
        finalTitle: 'You completed the corporate carbon management course',
        finalBullets: ['Carbon management is now connected to sales, finance, and supply chains.', 'ESG requires evidence, not slogans.', 'Scope 1, 2, and 3 show where data must be collected.', 'MRV makes carbon data auditable.', 'The first practical goal is a repeatable monthly data process.']
      },
      'th-TH': {
        kicker: 'หลักสูตรภาคปฏิบัติสำหรับองค์กร',
        title: 'การจัดการคาร์บอนสำหรับองค์กร',
        sub: 'คาร์บอนไม่ใช่แค่เรื่องสิ่งแวดล้อม แต่เกี่ยวข้องกับการส่งออก การประมูล เงินทุน ความน่าเชื่อถือของซัพพลายเชน และความต่อเนื่องทางธุรกิจ',
        chapters: [
          { title: '1. ทำไมบริษัทต้องจัดการคาร์บอนตอนนี้', body: 'ลูกค้าระดับโลก นักลงทุน และหน่วยงานกำกับต้องการหลักฐานข้อมูลคาร์บอนมากขึ้น หากไม่มีข้อมูลที่เชื่อถือได้ บริษัทอาจเสียโอกาสส่งออก สถานะซัพพลายเออร์ คะแนนจัดซื้อภาครัฐ หรือเงื่อนไขทางการเงิน', cards: [['ความเสี่ยงธุรกิจ','ข้อมูลคาร์บอนมีผลต่อยอดขาย การจัดซื้อ เงินกู้ และการตรวจสอบจากนักลงทุน'],['การค้าและ CBAM','สินค้าคาร์บอนสูงอาจมีต้นทุนเพิ่มเมื่อส่งออกไปตลาดที่มีกฎระเบียบ'],['แรงกดดันซัพพลายเชน','ลูกค้ารายใหญ่ขอข้อมูลการปล่อยเพื่อจัดการ Scope 3'],['กฎปฏิบัติ','จัดการข้อมูลคาร์บอนเหมือนข้อมูลการเงิน: วัด ตรวจสอบ และติดตามได้']], quiz: 'ประเด็นสำคัญ: การจัดการคาร์บอนคือความสามารถในการแข่งขันของธุรกิจ' },
          { title: '2. ESG ในการทำงานจริง', body: 'ESG คือสิ่งแวดล้อม สังคม และธรรมาภิบาล สำหรับทีมปฏิบัติการ ESG คือระบบบริหารที่พิสูจน์ว่าบริษัทจัดการข้อมูลสิ่งแวดล้อม ความปลอดภัย การปฏิบัติตามกฎ และการตัดสินใจอย่างไร', cards: [['Environment','พลังงาน การปล่อย ของเสีย น้ำ และแผนลดคาร์บอน'],['Social','ความปลอดภัย แรงงาน ซัพพลายเออร์ ชุมชน และลูกค้า'],['Governance','การกำกับดูแล จริยธรรม การควบคุมภายใน และ audit trail'],['Carbon link','ข้อมูลคาร์บอนเป็นส่วนที่วัดได้ชัดเจนที่สุดของ ESG']], quiz: 'ประเด็นสำคัญ: ESG จะน่าเชื่อถือเมื่อมีข้อมูลและหลักฐานรองรับ' },
          { title: '3. Scope 1, 2, 3', body: 'การปล่อยขององค์กรแบ่งเป็น Scope 1, Scope 2 และ Scope 3 เพื่อดูว่าการปล่อยเกิดที่ไหนและต้องเก็บข้อมูลอะไร', cards: [['Scope 1','การปล่อยโดยตรงจากเชื้อเพลิง รถ หม้อไอน้ำ หรือกระบวนการของบริษัท'],['Scope 2','การปล่อยทางอ้อมจากไฟฟ้า ไอน้ำ ความร้อน หรือความเย็นที่ซื้อ'],['Scope 3','การปล่อยในห่วงโซ่คุณค่าจากซัพพลายเออร์ โลจิสติกส์ การเดินทาง การใช้สินค้า และการกำจัด'],['เริ่มต้น','เริ่มจากข้อมูลที่มีอยู่: เชื้อเพลิง ไฟฟ้า ยานพาหนะ และซัพพลายเออร์หลัก']], quiz: 'ประเด็นสำคัญ: Scope 3 มักใหญ่และยากที่สุด จึงต้องบริหารข้อมูลซัพพลายเออร์' },
          { title: '4. MRV: วัดผล รายงาน ตรวจสอบ', body: 'MRV คือวินัยการทำงานสำหรับข้อมูลคาร์บอนที่น่าเชื่อถือ Measurement คือเก็บข้อมูล Reporting คือจัดข้อมูลให้ใช้ได้ Verification คือยืนยันว่าข้อมูลน่าเชื่อถือ', cards: [['Measurement','เก็บข้อมูลพลังงาน โมบิลิตี้ การผลิต เซนเซอร์ และกิจกรรม'],['Reporting','แปลงข้อมูลเป็นการปล่อย การลด และตัวชี้วัดธุรกิจ'],['Verification','ตรวจ hash แหล่งที่มา วิธีคำนวณ และประวัติ audit'],['คุณค่าธุรกิจ','ข้อมูลที่ตรวจสอบได้ลดความเสี่ยง greenwashing และช่วยรายงาน ESG']], quiz: 'ประเด็นสำคัญ: MRV เปลี่ยนข้อมูลปฏิบัติการให้เป็นหลักฐานที่เชื่อถือได้' },
          { title: '5. การจัดการคาร์บอนซัพพลายเชน', body: 'บริษัทจำนวนมากถูกลูกค้าขอข้อมูลคาร์บอน เพราะลูกค้าต้องรายงาน Scope 3 ของตนเอง ซัพพลายเออร์ที่ให้ข้อมูลน่าเชื่อถือได้จึงมีความได้เปรียบ', cards: [['คำขอลูกค้า','ลูกค้าอาจขอข้อมูลพลังงาน เชื้อเพลิง โลจิสติกส์ และคาร์บอนสินค้า'],['แม่แบบข้อมูล','ใช้แบบสอบถามและ data dictionary ที่สม่ำเสมอ'],['หลักฐาน','เก็บใบแจ้งหนี้ มิเตอร์ API log และเวอร์ชันการคำนวณ'],['โอกาส','ข้อมูลคาร์บอนที่ดีเป็นข้อได้เปรียบด้านการขาย']], quiz: 'ประเด็นสำคัญ: ข้อมูลคาร์บอนช่วยรักษาลูกค้าและชนะลูกค้าใหม่ได้' },
          { title: '6. สิ่งที่ควรทำก่อน', body: 'บริษัทไม่จำเป็นต้องแก้ทุกอย่างในวันแรก ขั้นแรกคือสร้างกระบวนการข้อมูลซ้ำได้และกำหนดเจ้าของข้อมูลให้ชัดเจน', cards: [['ขั้น 1','ระบุแหล่งปล่อย: เชื้อเพลิง ไฟฟ้า รถ โรงงาน โลจิสติกส์ ซัพพลายเออร์'],['ขั้น 2','กำหนดเจ้าของข้อมูลแต่ละแหล่ง'],['ขั้น 3','เก็บข้อมูลรายเดือนและหลักฐาน'],['ขั้น 4','คำนวณด้วย emission factor ที่มีเวอร์ชัน'],['ขั้น 5','ตรวจทานและเตรียมรายงานให้ลูกค้า ผู้ตรวจสอบ และผู้บริหาร']], quiz: 'ประเด็นสำคัญ: เริ่มจาก MRV รายเดือนที่ทำซ้ำได้ แล้วค่อยขยาย' }
        ],
        finalTitle: 'คุณเรียนจบหลักสูตรการจัดการคาร์บอนสำหรับองค์กรแล้ว',
        finalBullets: ['คาร์บอนเกี่ยวข้องกับยอดขาย การเงิน และซัพพลายเชน', 'ESG ต้องมีหลักฐาน ไม่ใช่คำขวัญ', 'Scope 1, 2, 3 บอกว่าต้องเก็บข้อมูลที่ใด', 'MRV ทำให้ข้อมูลคาร์บอนตรวจสอบได้', 'เป้าหมายแรกคือกระบวนการข้อมูลรายเดือนที่ทำซ้ำได้']
      },
      'vi-VN': {
        kicker: 'Khóa thực hành cho doanh nghiệp',
        title: 'Thực hành quản lý carbon doanh nghiệp',
        sub: 'Carbon không còn là chủ đề môi trường đơn thuần. Với doanh nghiệp, nó gắn với xuất khẩu, đấu thầu, tài chính, niềm tin chuỗi cung ứng và khả năng duy trì kinh doanh.',
        chapters: [
          { title: '1. Vì sao doanh nghiệp phải quản lý carbon ngay', body: 'Khách hàng toàn cầu, nhà đầu tư và cơ quan quản lý ngày càng yêu cầu dữ liệu carbon có bằng chứng. Không có dữ liệu đáng tin cậy, doanh nghiệp có thể mất cơ hội xuất khẩu, vị trí nhà cung cấp, điểm mua sắm công hoặc lợi thế tài chính.', cards: [['Rủi ro kinh doanh','Dữ liệu carbon ảnh hưởng đến bán hàng, mua sắm, khoản vay và thẩm định đầu tư'],['CBAM và thương mại','Sản phẩm phát thải cao có thể chịu chi phí carbon khi xuất khẩu'],['Yêu cầu chuỗi cung ứng','Khách hàng lớn cần dữ liệu phát thải để quản lý Scope 3'],['Nguyên tắc','Quản lý dữ liệu carbon như dữ liệu tài chính: đo, kiểm tra và truy xuất']], quiz: 'Điểm chính: quản lý carbon là năng lực cạnh tranh kinh doanh.' },
          { title: '2. ESG trong thực tế', body: 'ESG là Environment, Social, Governance. Với đội vận hành, ESG là hệ thống quản trị chứng minh doanh nghiệp quản lý dữ liệu môi trường, an toàn, tuân thủ và ra quyết định như thế nào.', cards: [['Environment','Năng lượng, phát thải, chất thải, nước và kế hoạch giảm phát thải'],['Social','An toàn, lao động, nhà cung cấp, cộng đồng và khách hàng'],['Governance','Giám sát, đạo đức, kiểm soát nội bộ và audit trail'],['Liên kết carbon','Dữ liệu carbon là phần dễ đo lường nhất của ESG']], quiz: 'Điểm chính: ESG chỉ đáng tin khi có dữ liệu và bằng chứng.' },
          { title: '3. Scope 1, 2, 3', body: 'Phát thải doanh nghiệp được chia thành Scope 1, Scope 2 và Scope 3. Cấu trúc này giúp xác định phát thải xảy ra ở đâu và cần thu thập dữ liệu gì.', cards: [['Scope 1','Phát thải trực tiếp từ nhiên liệu, xe, lò hơi hoặc quy trình thuộc sở hữu công ty'],['Scope 2','Phát thải gián tiếp từ điện, hơi, nhiệt hoặc làm mát mua vào'],['Scope 3','Phát thải chuỗi giá trị từ nhà cung cấp, logistics, công tác, sử dụng sản phẩm và thải bỏ'],['Bắt đầu','Bắt đầu với dữ liệu sẵn có: nhiên liệu, điện, xe và nhà cung cấp chính']], quiz: 'Điểm chính: Scope 3 thường lớn và khó nhất, nên quản lý dữ liệu nhà cung cấp rất quan trọng.' },
          { title: '4. MRV: Đo lường, Báo cáo, Xác minh', body: 'MRV là quy trình vận hành cho dữ liệu carbon đáng tin cậy. Measurement thu thập dữ liệu, Reporting tổ chức dữ liệu thành báo cáo, Verification kiểm tra độ tin cậy.', cards: [['Measurement','Thu thập dữ liệu năng lượng, di chuyển, sản xuất, cảm biến và hoạt động'],['Reporting','Chuyển dữ liệu thành phát thải, giảm phát thải và chỉ số kinh doanh'],['Verification','Kiểm tra hash, nguồn, phương pháp, tính toán và lịch sử audit'],['Giá trị kinh doanh','Dữ liệu xác minh được giảm rủi ro greenwashing và hỗ trợ công bố ESG']], quiz: 'Điểm chính: MRV biến dữ liệu vận hành thành bằng chứng đáng tin cậy.' },
          { title: '5. Quản lý carbon chuỗi cung ứng', body: 'Nhiều công ty bị khách hàng yêu cầu nộp dữ liệu carbon vì khách hàng phải báo cáo Scope 3 của họ. Nhà cung cấp cung cấp được dữ liệu đáng tin sẽ cạnh tranh hơn.', cards: [['Yêu cầu khách hàng','Khách hàng có thể yêu cầu dữ liệu năng lượng, nhiên liệu, logistics và carbon sản phẩm'],['Mẫu dữ liệu','Dùng questionnaire và data dictionary thống nhất'],['Bằng chứng','Lưu hóa đơn, chỉ số đồng hồ, log API và phiên bản tính toán'],['Cơ hội','Dữ liệu carbon tốt có thể trở thành lợi thế bán hàng']], quiz: 'Điểm chính: dữ liệu carbon giúp giữ khách hàng và thắng khách hàng mới.' },
          { title: '6. Việc cần làm trước', body: 'Doanh nghiệp không cần giải quyết mọi thứ ngay ngày đầu. Bước thực tế đầu tiên là tạo luồng dữ liệu lặp lại được và phân công chủ sở hữu rõ ràng.', cards: [['Bước 1','Liệt kê nguồn phát thải: nhiên liệu, điện, xe, nhà máy, logistics, nhà cung cấp'],['Bước 2','Gán người phụ trách từng nguồn dữ liệu'],['Bước 3','Thu thập dữ liệu hàng tháng và lưu bằng chứng'],['Bước 4','Tính toán bằng hệ số có version'],['Bước 5','Rà soát và chuẩn bị báo cáo cho khách hàng, kiểm toán và lãnh đạo']], quiz: 'Điểm chính: bắt đầu bằng quy trình MRV hàng tháng rồi mở rộng.' }
        ],
        finalTitle: 'Bạn đã hoàn thành khóa thực hành quản lý carbon doanh nghiệp',
        finalBullets: ['Quản lý carbon liên quan đến bán hàng, tài chính và chuỗi cung ứng.', 'ESG cần bằng chứng, không chỉ khẩu hiệu.', 'Scope 1, 2, 3 chỉ ra nơi cần thu thập dữ liệu.', 'MRV giúp dữ liệu carbon có thể kiểm toán.', 'Mục tiêu đầu tiên là quy trình dữ liệu hàng tháng lặp lại được.']
      },
      'zh-CN': {
        kicker: '企业实务课程',
        title: '企业碳管理实务',
        sub: '碳不再只是环境议题。对企业而言，它已经关系到出口、投标、融资、供应链信任和经营连续性。',
        chapters: [
          { title: '1. 为什么企业现在必须管理碳', body: '全球客户、投资者和监管机构越来越要求企业证明碳数据。如果没有可信数据，企业可能失去出口机会、供应商资格、公共采购分数或融资优势。', cards: [['业务风险','碳数据影响销售、采购、贷款和投资尽调'],['CBAM 与贸易','高碳产品出口到受监管市场时可能承担额外碳成本'],['供应链要求','大型客户要求供应商提供排放数据以管理 Scope 3'],['实务原则','像管理财务数据一样管理碳数据：测量、审核、可追溯']], quiz: '重点：碳管理已经成为企业竞争力问题。' },
          { title: '2. ESG 的实务含义', body: 'ESG 指环境、社会和治理。对运营团队而言，ESG 不是海报或口号，而是证明企业如何管理环境数据、安全、合规和决策的管理体系。', cards: [['环境','能源、排放、废弃物、水和减排计划'],['社会','安全、劳工、供应商、社区和客户责任'],['治理','董事会监督、伦理、内部控制和审计轨迹'],['碳的连接','碳数据是 ESG 中最容易量化的部分之一']], quiz: '重点：ESG 只有在数据和证据支撑下才可信。' },
          { title: '3. Scope 1、2、3', body: '企业排放分为 Scope 1、Scope 2 和 Scope 3。这个结构帮助企业识别排放发生在哪里，以及必须收集什么数据。', cards: [['Scope 1','来自企业自有燃料、车辆、锅炉或工艺的直接排放'],['Scope 2','来自外购电力、蒸汽、供热或制冷的间接排放'],['Scope 3','来自供应商、物流、差旅、产品使用和处置的价值链排放'],['第一步','从已有数据开始：燃料、电力、车辆和主要供应商']], quiz: '重点：Scope 3 通常最大也最难，因此供应商数据管理很重要。' },
          { title: '4. MRV：测量、报告、核证', body: 'MRV 是可信碳数据的运营纪律。测量负责采集数据，报告负责组织数据，核证负责检查数据是否可靠。', cards: [['测量','采集能源、移动、生产、传感器和活动数据'],['报告','将数据转化为排放、减排和业务指标'],['核证','检查哈希、来源、方法、计算和审计历史'],['业务价值','经核证的数据可降低漂绿风险并支持 ESG 披露']], quiz: '重点：MRV 将原始运营数据转化为可信证据。' },
          { title: '5. 供应链碳管理', body: '很多企业会被客户要求提交碳数据，因为客户需要报告自己的 Scope 3 排放。能够提供可靠数据的供应商更有竞争力。', cards: [['客户请求','客户可能要求能源、燃料、物流和产品碳数据'],['数据模板','使用统一问卷和数据字典'],['证据','保存发票、仪表读数、API 日志和计算版本'],['机会','高质量碳数据可以成为销售优势']], quiz: '重点：碳数据可以帮助保留客户并赢得新客户。' },
          { title: '6. 现在先做什么', body: '企业不需要第一天就解决所有问题。务实的第一步是建立可重复的数据流程，并明确数据负责人。', cards: [['步骤 1','列出排放源：燃料、电力、车辆、工厂、物流、供应商'],['步骤 2','确定每个数据源的负责人'],['步骤 3','每月收集数据并保存证据'],['步骤 4','使用有版本的排放因子进行计算'],['步骤 5','审查结果并为客户、审计方和管理层准备报告']], quiz: '重点：从简单的月度 MRV 流程开始，然后扩展。' }
        ],
        finalTitle: '你已完成企业碳管理实务课程',
        finalBullets: ['碳管理关系到销售、融资和供应链。', 'ESG 需要证据，而不是口号。', 'Scope 1、2、3 指明数据收集位置。', 'MRV 让碳数据可审计。', '第一个目标是建立可重复的月度数据流程。']
      }
    },
    '03_enterprise.html': {
      'en-US': {
        kicker: 'Enterprise Strategy Course',
        title: 'Enterprise Carbon Strategy',
        sub: 'For large enterprises, carbon is not only a compliance cost. It is a strategic system for regulation, supply-chain resilience, capital access, brand value, and long-term competitiveness.',
        chapters: [
          { title: '1. Global ESG regulation is becoming operational', body: 'Regulation is moving from voluntary disclosure to mandatory reporting and cost exposure. CSRD, CBAM, climate disclosure, and national ESG rules force enterprises to manage carbon data at group level.', cards: [['CSRD','Sustainability disclosure becomes part of formal corporate reporting.'],['CBAM','Carbon intensity can affect export cost and pricing strategy.'],['Climate disclosure','Investors expect quantified climate risk and transition plans.'],['Strategic meaning','Carbon data must be governed like finance, legal, and risk data.']], quiz: 'Key point: carbon regulation is now an operating requirement, not a public-relations issue.' },
          { title: '2. Supply-chain carbon risk', body: 'Large enterprises often have most emissions in Scope 3. The company cannot meet Net Zero targets unless suppliers, logistics, and product-use emissions are measured and managed.', cards: [['Supplier risk','Suppliers without carbon data increase reporting uncertainty.'],['Procurement leverage','Carbon criteria can be included in supplier selection.'],['Resilience','A low-carbon supply chain reduces regulatory and brand risk.'],['Partnership','Support suppliers with templates, tools, and MRV systems.']], quiz: 'Key point: supply-chain carbon capability becomes enterprise resilience.' },
          { title: '3. Integrated carbon data strategy', body: 'Enterprise carbon strategy requires data integration across factories, logistics, energy, finance, ESG teams, and suppliers. Fragmented spreadsheets are not enough for audit-grade reporting.', cards: [['Single data model','Use standardized source types, units, factors, and methodology versions.'],['Evidence layer','Each result should link back to packet, evidence, MRV, and audit data.'],['Executive view','Management needs carbon, finance, and risk indicators together.'],['AI MRV','AI can explain, detect anomalies, and forecast, but it must rely on verified data.']], quiz: 'Key point: the enterprise advantage is an integrated, auditable carbon data infrastructure.' },
          { title: '4. Carbon credit and internal carbon price strategy', body: 'Carbon credits should not be treated as a shortcut. Enterprises need a hierarchy: reduce first, verify data, use high-quality credits only for residual emissions, and set an internal carbon price for decisions.', cards: [['Reduce first','Operational reduction has stronger credibility than offset-only claims.'],['Quality filter','Credits need additionality, permanence, leakage control, and verification.'],['Internal price','A carbon price helps compare investments and operating choices.'],['Governance','Claims must be approved and documented to avoid greenwashing.']], quiz: 'Key point: credit strategy must be governed by quality, evidence, and reduction priority.' },
          { title: '5. AI-based reduction strategy', body: 'AI becomes valuable when it helps operators act: charging at lower-carbon hours, matching solar production, reducing idle miles, prioritizing capex, and forecasting missed targets before they happen.', cards: [['Forecast','Predict CO₂e, cost, and revenue impacts over 30 days to one year.'],['Optimization','Recommend charging, solar, ESS, fleet, and route actions.'],['Decision support','Compare scenarios by ROI, payback, and risk.'],['Control loop','Track whether recommended actions actually improved results.']], quiz: 'Key point: AI should turn trusted carbon data into operational decisions.' }
        ],
        finalTitle: 'You completed the enterprise carbon strategy course',
        finalBullets: ['Carbon regulation is moving into core operations.', 'Scope 3 supply-chain data is a strategic risk area.', 'Integrated carbon data infrastructure is essential.', 'Carbon credits require strong governance and quality filters.', 'AI MRV should support decisions, not create unverified claims.']
      },
      'th-TH': {
        kicker: 'หลักสูตรกลยุทธ์องค์กรขนาดใหญ่',
        title: 'กลยุทธ์คาร์บอนสำหรับองค์กรขนาดใหญ่',
        sub: 'สำหรับองค์กรขนาดใหญ่ คาร์บอนไม่ใช่แค่ต้นทุน compliance แต่เป็นระบบกลยุทธ์ด้านกฎระเบียบ ซัพพลายเชน เงินทุน แบรนด์ และความสามารถแข่งขันระยะยาว',
        chapters: [
          { title: '1. กฎ ESG โลกกำลังกลายเป็นงานปฏิบัติการ', body: 'กฎระเบียบกำลังเปลี่ยนจากการเปิดเผยสมัครใจไปสู่การรายงานภาคบังคับและต้นทุนจริง CSRD, CBAM, climate disclosure และกฎ ESG ระดับประเทศบังคับให้องค์กรจัดการข้อมูลคาร์บอนระดับกลุ่ม', cards: [['CSRD','รายงานความยั่งยืนกลายเป็นส่วนหนึ่งของรายงานองค์กรอย่างเป็นทางการ'],['CBAM','ความเข้มข้นคาร์บอนมีผลต่อต้นทุนส่งออกและกลยุทธ์ราคา'],['Climate disclosure','นักลงทุนต้องการความเสี่ยงภูมิอากาศและแผน transition ที่เป็นตัวเลข'],['ความหมายเชิงกลยุทธ์','ข้อมูลคาร์บอนต้องถูกกำกับเหมือนข้อมูลการเงิน กฎหมาย และความเสี่ยง']], quiz: 'ประเด็นสำคัญ: กฎคาร์บอนคือข้อกำหนดด้านปฏิบัติการ ไม่ใช่ PR' },
          { title: '2. ความเสี่ยงคาร์บอนในซัพพลายเชน', body: 'องค์กรขนาดใหญ่มักมีการปล่อยส่วนใหญ่ใน Scope 3 หากไม่วัดและจัดการซัพพลายเออร์ โลจิสติกส์ และการใช้สินค้า เป้าหมาย Net Zero จะสำเร็จไม่ได้', cards: [['ความเสี่ยงซัพพลายเออร์','ซัพพลายเออร์ไม่มีข้อมูลคาร์บอนทำให้รายงานไม่แน่นอน'],['อำนาจจัดซื้อ','เพิ่มเกณฑ์คาร์บอนในการคัดเลือกซัพพลายเออร์'],['ความยืดหยุ่น','ซัพพลายเชนคาร์บอนต่ำลดความเสี่ยงกฎระเบียบและแบรนด์'],['ความร่วมมือ','สนับสนุนซัพพลายเออร์ด้วย template, tool และ MRV']], quiz: 'ประเด็นสำคัญ: ความสามารถคาร์บอนของซัพพลายเชนคือ resilience ขององค์กร' },
          { title: '3. กลยุทธ์ข้อมูลคาร์บอนแบบรวมศูนย์', body: 'กลยุทธ์คาร์บอนองค์กรต้องรวมข้อมูลจากโรงงาน โลจิสติกส์ พลังงาน การเงิน ESG และซัพพลายเออร์ Spreadsheet กระจัดกระจายไม่พอสำหรับรายงานที่ตรวจสอบได้', cards: [['โมเดลข้อมูลเดียว','กำหนด source type, unit, factor และ methodology version ให้มาตรฐาน'],['Evidence layer','ทุกผลลัพธ์ต้องย้อนกลับไป packet, evidence, MRV และ audit ได้'],['มุมมองผู้บริหาร','ผู้บริหารต้องเห็นคาร์บอน การเงิน และความเสี่ยงร่วมกัน'],['AI MRV','AI อธิบาย ตรวจ anomaly และพยากรณ์ได้ แต่ต้องพึ่งข้อมูลที่ตรวจสอบแล้ว']], quiz: 'ประเด็นสำคัญ: ความได้เปรียบองค์กรคือโครงสร้างข้อมูลคาร์บอนที่ตรวจสอบได้' },
          { title: '4. กลยุทธ์ carbon credit และ internal carbon price', body: 'Carbon credit ไม่ใช่ทางลัด องค์กรต้องลดก่อน ตรวจสอบข้อมูล ใช้เครดิตคุณภาพสูงเฉพาะส่วนที่เหลือ และตั้งราคา carbon ภายในเพื่อการตัดสินใจ', cards: [['ลดก่อน','การลดจริงมีความน่าเชื่อถือกว่าการ offset อย่างเดียว'],['ตัวกรองคุณภาพ','เครดิตต้องมี additionality, permanence, leakage control และ verification'],['ราคาคาร์บอนภายใน','ช่วยเปรียบเทียบการลงทุนและทางเลือกดำเนินงาน'],['Governance','การกล่าวอ้างต้องได้รับอนุมัติและบันทึกเพื่อหลีกเลี่ยง greenwashing']], quiz: 'ประเด็นสำคัญ: กลยุทธ์เครดิตต้องกำกับด้วยคุณภาพ หลักฐาน และการลดก่อน' },
          { title: '5. กลยุทธ์ลดคาร์บอนด้วย AI', body: 'AI มีคุณค่าเมื่อช่วยให้เกิดการกระทำ เช่น ชาร์จในช่วงคาร์บอนต่ำ จับคู่พลังงานแสงอาทิตย์ ลดระยะวิ่งเปล่า จัดลำดับ CAPEX และเตือนเป้าหมายพลาดล่วงหน้า', cards: [['Forecast','พยากรณ์ CO₂e ต้นทุน และรายได้ 30 วันถึง 1 ปี'],['Optimization','แนะนำ charging, solar, ESS, fleet และ route actions'],['Decision support','เปรียบเทียบ scenario ด้วย ROI, payback และ risk'],['Control loop','ติดตามว่าคำแนะนำทำให้ผลลัพธ์ดีขึ้นจริงหรือไม่']], quiz: 'ประเด็นสำคัญ: AI ต้องเปลี่ยนข้อมูลคาร์บอนที่เชื่อถือได้ให้เป็นการตัดสินใจปฏิบัติการ' }
        ],
        finalTitle: 'คุณเรียนจบหลักสูตรกลยุทธ์คาร์บอนองค์กรแล้ว',
        finalBullets: ['กฎคาร์บอนกำลังเข้าสู่ core operation', 'Scope 3 เป็นความเสี่ยงเชิงกลยุทธ์', 'โครงสร้างข้อมูลคาร์บอนแบบรวมศูนย์จำเป็นมาก', 'Carbon credit ต้องมี governance และ quality filter', 'AI MRV ต้องสนับสนุนการตัดสินใจ ไม่ใช่สร้าง claim ที่ไม่มีหลักฐาน']
      },
      'vi-VN': {
        kicker: 'Khóa chiến lược cho tập đoàn',
        title: 'Chiến lược carbon cho tập đoàn',
        sub: 'Với tập đoàn lớn, carbon không chỉ là chi phí tuân thủ. Nó là hệ thống chiến lược cho quy định, khả năng chống chịu chuỗi cung ứng, tiếp cận vốn, thương hiệu và cạnh tranh dài hạn.',
        chapters: [
          { title: '1. Quy định ESG toàn cầu đang trở thành vận hành', body: 'Quy định chuyển từ tự nguyện sang báo cáo bắt buộc và chi phí thực. CSRD, CBAM, công bố khí hậu và quy định ESG quốc gia buộc tập đoàn quản lý dữ liệu carbon cấp tập đoàn.', cards: [['CSRD','Công bố bền vững trở thành một phần của báo cáo doanh nghiệp chính thức'],['CBAM','Cường độ carbon có thể ảnh hưởng đến chi phí xuất khẩu và giá bán'],['Công bố khí hậu','Nhà đầu tư yêu cầu rủi ro khí hậu và kế hoạch chuyển đổi có định lượng'],['Ý nghĩa chiến lược','Dữ liệu carbon phải được quản trị như tài chính, pháp lý và rủi ro']], quiz: 'Điểm chính: quy định carbon là yêu cầu vận hành, không phải PR.' },
          { title: '2. Rủi ro carbon chuỗi cung ứng', body: 'Tập đoàn lớn thường có phần lớn phát thải ở Scope 3. Không thể đạt Net Zero nếu không đo và quản lý nhà cung cấp, logistics và phát thải từ sử dụng sản phẩm.', cards: [['Rủi ro nhà cung cấp','Nhà cung cấp thiếu dữ liệu carbon làm tăng bất định báo cáo'],['Đòn bẩy mua sắm','Có thể đưa tiêu chí carbon vào lựa chọn nhà cung cấp'],['Khả năng chống chịu','Chuỗi cung ứng carbon thấp giảm rủi ro quy định và thương hiệu'],['Hợp tác','Hỗ trợ nhà cung cấp bằng template, công cụ và hệ thống MRV']], quiz: 'Điểm chính: năng lực carbon của chuỗi cung ứng là khả năng chống chịu của tập đoàn.' },
          { title: '3. Chiến lược dữ liệu carbon tích hợp', body: 'Chiến lược carbon cần tích hợp dữ liệu từ nhà máy, logistics, năng lượng, tài chính, ESG và nhà cung cấp. Spreadsheet rời rạc không đủ cho báo cáo kiểm toán được.', cards: [['Mô hình dữ liệu chung','Chuẩn hóa source type, đơn vị, hệ số và phiên bản phương pháp'],['Evidence layer','Mỗi kết quả phải truy ngược tới packet, evidence, MRV và audit'],['Góc nhìn lãnh đạo','Lãnh đạo cần thấy carbon, tài chính và rủi ro cùng nhau'],['AI MRV','AI có thể giải thích, phát hiện bất thường và dự báo nhưng phải dựa trên dữ liệu đã xác minh']], quiz: 'Điểm chính: lợi thế của tập đoàn là hạ tầng dữ liệu carbon tích hợp và kiểm toán được.' },
          { title: '4. Chiến lược tín chỉ carbon và giá carbon nội bộ', body: 'Carbon credit không phải đường tắt. Tập đoàn cần ưu tiên giảm phát thải, xác minh dữ liệu, chỉ dùng tín chỉ chất lượng cao cho phần còn lại và đặt giá carbon nội bộ cho quyết định.', cards: [['Giảm trước','Giảm vận hành đáng tin hơn tuyên bố chỉ dựa trên offset'],['Bộ lọc chất lượng','Tín chỉ cần additionality, permanence, kiểm soát leakage và verification'],['Giá carbon nội bộ','Giúp so sánh đầu tư và lựa chọn vận hành'],['Governance','Tuyên bố phải được phê duyệt và lưu bằng chứng để tránh greenwashing']], quiz: 'Điểm chính: chiến lược tín chỉ phải dựa trên chất lượng, bằng chứng và ưu tiên giảm phát thải.' },
          { title: '5. Chiến lược giảm phát thải bằng AI', body: 'AI có giá trị khi giúp vận hành hành động: sạc vào giờ carbon thấp hơn, khớp sản lượng mặt trời, giảm km rỗng, ưu tiên CAPEX và dự báo rủi ro trượt mục tiêu.', cards: [['Forecast','Dự báo CO₂e, chi phí và doanh thu từ 30 ngày đến 1 năm'],['Optimization','Khuyến nghị charging, solar, ESS, fleet và route actions'],['Decision support','So sánh kịch bản theo ROI, payback và risk'],['Control loop','Theo dõi khuyến nghị có cải thiện kết quả thật không']], quiz: 'Điểm chính: AI phải biến dữ liệu carbon đáng tin thành quyết định vận hành.' }
        ],
        finalTitle: 'Bạn đã hoàn thành khóa chiến lược carbon cho tập đoàn',
        finalBullets: ['Quy định carbon đã đi vào vận hành cốt lõi.', 'Dữ liệu Scope 3 là rủi ro chiến lược.', 'Hạ tầng dữ liệu carbon tích hợp là bắt buộc.', 'Carbon credit cần governance và bộ lọc chất lượng.', 'AI MRV phải hỗ trợ quyết định, không tạo claim chưa xác minh.']
      },
      'zh-CN': {
        kicker: '大型企业战略课程',
        title: '大型企业碳战略',
        sub: '对大型企业而言，碳不只是合规成本，而是连接监管、供应链韧性、资本、品牌价值和长期竞争力的战略系统。',
        chapters: [
          { title: '1. 全球 ESG 监管正在运营化', body: '监管正从自愿披露转向强制报告和实际成本暴露。CSRD、CBAM、气候披露和国家 ESG 规则要求企业在集团层面管理碳数据。', cards: [['CSRD','可持续披露成为正式企业报告的一部分'],['CBAM','碳强度会影响出口成本和定价策略'],['气候披露','投资者要求量化气候风险和转型计划'],['战略含义','碳数据必须像财务、法务和风险数据一样治理']], quiz: '重点：碳监管已经是运营要求，而不是公关议题。' },
          { title: '2. 供应链碳风险', body: '大型企业的大部分排放往往在 Scope 3。如果供应商、物流和产品使用阶段排放没有被测量和管理，企业无法实现净零目标。', cards: [['供应商风险','缺乏碳数据的供应商会增加报告不确定性'],['采购杠杆','可以把碳标准纳入供应商选择'],['韧性','低碳供应链降低监管和品牌风险'],['合作','用模板、工具和 MRV 系统支持供应商']], quiz: '重点：供应链碳能力就是企业韧性。' },
          { title: '3. 碳数据整合战略', body: '企业碳战略需要整合工厂、物流、能源、财务、ESG 团队和供应商数据。分散表格无法支撑审计级报告。', cards: [['统一数据模型','标准化 source type、单位、因子和方法学版本'],['证据层','每个结果都应追溯到 packet、evidence、MRV 和 audit 数据'],['管理层视图','管理层需要同时看到碳、财务和风险指标'],['AI MRV','AI 可以解释、发现异常和预测，但必须依赖已验证数据']], quiz: '重点：企业优势来自整合且可审计的碳数据基础设施。' },
          { title: '4. 碳信用与内部碳价战略', body: '碳信用不应被当作捷径。企业需要先减排，再验证数据，只将高质量信用用于剩余排放，并设置内部碳价辅助决策。', cards: [['先减排','运营减排比只依赖抵消声明更可信'],['质量过滤','信用需要额外性、持久性、泄漏控制和核证'],['内部碳价','帮助比较投资和运营选择'],['治理','所有声明都要审批并留存文件，避免漂绿']], quiz: '重点：碳信用战略必须由质量、证据和减排优先级治理。' },
          { title: '5. AI 驱动的减排战略', body: 'AI 的价值在于帮助运营采取行动：在低碳时段充电、匹配太阳能发电、减少空驶、排序资本开支，并提前预测目标偏离。', cards: [['预测','预测 30 天到 1 年的 CO₂e、成本和收入影响'],['优化','推荐充电、太阳能、ESS、车队和路线行动'],['决策支持','按 ROI、回收期和风险比较情景'],['闭环','追踪推荐行动是否真正改善结果']], quiz: '重点：AI 应把可信碳数据转化为运营决策。' }
        ],
        finalTitle: '你已完成大型企业碳战略课程',
        finalBullets: ['碳监管正在进入核心运营。', 'Scope 3 供应链数据是战略风险。', '整合碳数据基础设施必不可少。', '碳信用需要治理和质量过滤。', 'AI MRV 应支持决策，而不是制造未经验证的声明。']
      }
    },
    '05_investor.html': {
      'en-US': {
        kicker: 'Investor Course',
        title: 'Carbon Market Investment Analysis',
        sub: 'Carbon is becoming an asset market. Investors need to understand project quality, MRV reliability, credit readiness, risk, pricing, and exit pathways.',
        chapters: [
          { title: '1. Carbon as a new asset class', body: 'Carbon markets turn verified emission reductions into financial value. The key question for investors is not only how much CO₂e is reduced, but whether that reduction is real, additional, verified, and monetizable.', cards: [['Asset logic','Verified reductions can become carbon asset candidates or credits.'],['Market types','Compliance markets and voluntary markets use different rules and prices.'],['Quality premium','High-quality MRV and credible methodology can command better value.'],['Investor lens','Evaluate data integrity before evaluating upside.']], quiz: 'Key point: carbon value depends on proof, not only volume.' },
          { title: '2. What determines credit value', body: 'Carbon credit value is driven by methodology, additionality, permanence, leakage risk, registry acceptance, buyer demand, and the credibility of MRV evidence.', cards: [['Additionality','Would the reduction have happened without the project?'],['Permanence','Will the reduction or removal last?'],['Leakage','Does the project increase emissions somewhere else?'],['Registry readiness','Can the project package satisfy verification and registry review?']], quiz: 'Key point: a large CO₂e number is weak without quality checks.' },
          { title: '3. MRV platform investment thesis', body: 'AI MRV platforms can become infrastructure for carbon asset markets because they collect data, seal evidence, calculate reductions, and prepare verification packages.', cards: [['Data moat','Operational data creates defensible insight.'],['Trust layer','Hashes, signatures, audit logs, and calibration records reduce manipulation risk.'],['Scalability','Config-driven methodology allows multiple sectors and countries.'],['Revenue model','SaaS, MRV service fees, reporting, verification support, and partner integrations.']], quiz: 'Key point: the platform value is the trusted data pipeline.' },
          { title: '4. Investment risks', body: 'Investors must separate real carbon infrastructure from unverified claims. Main risks include data quality, weak methodology, regulatory changes, double counting, project execution, and buyer demand.', cards: [['Data risk','Missing or manipulated source data weakens asset quality.'],['Methodology risk','Wrong factors or outdated methods can invalidate estimates.'],['Regulatory risk','Rules may change by country and year.'],['Commercial risk','Carbon value must connect to paying customers or buyers.']], quiz: 'Key point: risk analysis must cover data, methodology, regulation, and revenue.' },
          { title: '5. Investor due diligence checklist', body: 'Before investing, confirm whether the platform can prove traceability from raw data to evidence, MRV, value, asset, report, and registry readiness.', cards: [['Traceability','Can every result be traced back to source data?'],['Verification','Is there a review workflow and evidence package?'],['Economics','Are cost savings, revenue, payback, and assumptions visible?'],['Replication','Can the model scale from one customer to many?']], quiz: 'Key point: invest in repeatable proof, not a one-off demo.' }
        ],
        finalTitle: 'You completed the carbon market investor course',
        finalBullets: ['Carbon assets require evidence and verification.', 'Credit value depends on quality, not only quantity.', 'AI MRV can be carbon market infrastructure.', 'Investors must evaluate data, methodology, regulatory, and commercial risk.', 'The strongest signal is repeatable customer data.']
      },
      'th-TH': {
        kicker: 'หลักสูตรนักลงทุน',
        title: 'การวิเคราะห์การลงทุนในตลาดคาร์บอน',
        sub: 'คาร์บอนกำลังกลายเป็นตลาดสินทรัพย์ นักลงทุนต้องเข้าใจคุณภาพโครงการ ความน่าเชื่อถือของ MRV ความพร้อมเครดิต ความเสี่ยง ราคา และทางออกการลงทุน',
        chapters: [
          { title: '1. คาร์บอนในฐานะสินทรัพย์ใหม่', body: 'ตลาดคาร์บอนเปลี่ยนการลดการปล่อยที่ตรวจสอบแล้วให้เป็นมูลค่าทางการเงิน นักลงทุนต้องดูไม่ใช่แค่ลดได้กี่ตัน แต่ต้องดูว่าจริง เพิ่มเติม ตรวจสอบได้ และสร้างรายได้ได้หรือไม่', cards: [['ตรรกะสินทรัพย์','การลดที่ตรวจสอบแล้วอาจเป็น carbon asset candidate หรือ credit'],['ประเภทตลาด','ตลาดกำกับและตลาดสมัครใจมีกฎและราคาต่างกัน'],['พรีเมียมคุณภาพ','MRV คุณภาพสูงและวิธีวิทยาน่าเชื่อถือช่วยเพิ่มมูลค่า'],['มุมนักลงทุน','ตรวจ data integrity ก่อนดู upside']], quiz: 'ประเด็นสำคัญ: มูลค่าคาร์บอนขึ้นกับหลักฐาน ไม่ใช่แค่ปริมาณ' },
          { title: '2. อะไรกำหนดมูลค่าเครดิต', body: 'มูลค่าเครดิตขึ้นกับ methodology, additionality, permanence, leakage risk, registry acceptance, demand และความน่าเชื่อถือของ MRV evidence', cards: [['Additionality','การลดจะเกิดขึ้นไหมถ้าไม่มีโครงการ?'],['Permanence','ผลการลดหรือการกักเก็บอยู่ได้นานไหม?'],['Leakage','โครงการทำให้ที่อื่นปล่อยเพิ่มไหม?'],['Registry readiness','แพ็กเกจโครงการพร้อมให้ผู้ตรวจและ registry พิจารณาหรือไม่?']], quiz: 'ประเด็นสำคัญ: ตัวเลข CO₂e ใหญ่แต่ไม่มี quality check จะอ่อนแอ' },
          { title: '3. Thesis การลงทุนในแพลตฟอร์ม MRV', body: 'แพลตฟอร์ม AI MRV อาจเป็นโครงสร้างพื้นฐานตลาดสินทรัพย์คาร์บอน เพราะเก็บข้อมูล ปิดผนึกหลักฐาน คำนวณการลด และเตรียม verification package', cards: [['Data moat','ข้อมูลปฏิบัติการสร้าง insight ที่ป้องกันได้'],['Trust layer','Hash, signature, audit log และ calibration ลดความเสี่ยงการบิดเบือน'],['Scalability','Methodology แบบ config-driven ขยายได้หลาย sector และประเทศ'],['Revenue model','SaaS, MRV fee, report, verification support และ partner integration']], quiz: 'ประเด็นสำคัญ: มูลค่าแพลตฟอร์มคือ trusted data pipeline' },
          { title: '4. ความเสี่ยงการลงทุน', body: 'นักลงทุนต้องแยกโครงสร้างพื้นฐานคาร์บอนจริงออกจาก claim ที่ไม่ตรวจสอบ ความเสี่ยงหลักคือคุณภาพข้อมูล วิธีวิทยา กฎระเบียบ double counting execution และ buyer demand', cards: [['Data risk','ข้อมูลต้นทางหายหรือถูกแก้ไขทำให้คุณภาพสินทรัพย์อ่อนลง'],['Methodology risk','Factor ผิดหรือวิธีเก่าทำให้ estimate ใช้ไม่ได้'],['Regulatory risk','กฎเปลี่ยนได้ตามประเทศและปี'],['Commercial risk','Carbon value ต้องเชื่อมกับลูกค้าหรือ buyer ที่จ่ายเงินจริง']], quiz: 'ประเด็นสำคัญ: ต้องวิเคราะห์ทั้งข้อมูล วิธีวิทยา กฎ และรายได้' },
          { title: '5. Checklist due diligence', body: 'ก่อนลงทุนต้องยืนยันว่าแพลตฟอร์มพิสูจน์ traceability จาก raw data ไป evidence, MRV, value, asset, report และ registry readiness ได้', cards: [['Traceability','ทุกผลลัพธ์ย้อนกลับไป source data ได้หรือไม่?'],['Verification','มี workflow ตรวจสอบและ evidence package หรือไม่?'],['Economics','เห็น saving, revenue, payback และ assumption หรือไม่?'],['Replication','โมเดลขยายจากลูกค้าหนึ่งรายไปหลายรายได้หรือไม่?']], quiz: 'ประเด็นสำคัญ: ลงทุนใน proof ที่ทำซ้ำได้ ไม่ใช่ demo ครั้งเดียว' }
        ],
        finalTitle: 'คุณเรียนจบหลักสูตรนักลงทุนตลาดคาร์บอนแล้ว',
        finalBullets: ['สินทรัพย์คาร์บอนต้องมีหลักฐานและการตรวจสอบ', 'มูลค่าเครดิตขึ้นกับคุณภาพ ไม่ใช่แค่ปริมาณ', 'AI MRV อาจเป็นโครงสร้างพื้นฐานตลาดคาร์บอน', 'นักลงทุนต้องประเมิน data, methodology, regulation และ commercial risk', 'สัญญาณที่แข็งแรงที่สุดคือข้อมูลลูกค้าจริงที่ทำซ้ำได้']
      },
      'vi-VN': {
        kicker: 'Khóa học cho nhà đầu tư',
        title: 'Phân tích đầu tư thị trường carbon',
        sub: 'Carbon đang trở thành một thị trường tài sản. Nhà đầu tư cần hiểu chất lượng dự án, độ tin cậy MRV, readiness tín chỉ, rủi ro, định giá và lộ trình thoái vốn.',
        chapters: [
          { title: '1. Carbon là lớp tài sản mới', body: 'Thị trường carbon biến giảm phát thải đã xác minh thành giá trị tài chính. Câu hỏi đầu tư không chỉ là giảm bao nhiêu CO₂e, mà là giảm đó có thật, có additionality, được xác minh và có thể thương mại hóa hay không.', cards: [['Logic tài sản','Giảm phát thải đã xác minh có thể thành carbon asset candidate hoặc credit'],['Loại thị trường','Thị trường bắt buộc và tự nguyện có luật và giá khác nhau'],['Premium chất lượng','MRV chất lượng và phương pháp đáng tin có thể tạo giá trị cao hơn'],['Góc nhìn đầu tư','Đánh giá data integrity trước upside']], quiz: 'Điểm chính: giá trị carbon phụ thuộc vào bằng chứng, không chỉ khối lượng.' },
          { title: '2. Yếu tố quyết định giá trị tín chỉ', body: 'Giá trị carbon credit phụ thuộc vào methodology, additionality, permanence, leakage risk, registry acceptance, nhu cầu người mua và độ tin cậy của MRV evidence.', cards: [['Additionality','Nếu không có dự án thì giảm phát thải có xảy ra không?'],['Permanence','Giảm hoặc lưu trữ carbon có bền vững không?'],['Leakage','Dự án có làm tăng phát thải nơi khác không?'],['Registry readiness','Hồ sơ dự án có đáp ứng verification và registry review không?']], quiz: 'Điểm chính: số CO₂e lớn nhưng thiếu kiểm tra chất lượng thì yếu.' },
          { title: '3. Luận điểm đầu tư nền tảng MRV', body: 'Nền tảng AI MRV có thể trở thành hạ tầng của thị trường tài sản carbon vì thu thập dữ liệu, niêm phong bằng chứng, tính giảm phát thải và chuẩn bị verification package.', cards: [['Data moat','Dữ liệu vận hành tạo insight có lợi thế phòng thủ'],['Trust layer','Hash, signature, audit log và calibration giảm rủi ro thao túng'],['Scalability','Methodology config-driven mở rộng nhiều ngành và quốc gia'],['Revenue model','SaaS, phí MRV, báo cáo, hỗ trợ xác minh và tích hợp đối tác']], quiz: 'Điểm chính: giá trị nền tảng là trusted data pipeline.' },
          { title: '4. Rủi ro đầu tư', body: 'Nhà đầu tư phải phân biệt hạ tầng carbon thật với tuyên bố chưa xác minh. Rủi ro chính gồm chất lượng dữ liệu, methodology yếu, thay đổi quy định, double counting, execution và nhu cầu người mua.', cards: [['Data risk','Dữ liệu nguồn thiếu hoặc bị chỉnh sửa làm yếu chất lượng tài sản'],['Methodology risk','Hệ số sai hoặc phương pháp lỗi thời làm mất giá trị ước tính'],['Regulatory risk','Quy định thay đổi theo quốc gia và năm'],['Commercial risk','Carbon value phải kết nối với khách hàng hoặc người mua trả tiền thật']], quiz: 'Điểm chính: phân tích rủi ro phải bao gồm dữ liệu, phương pháp, quy định và doanh thu.' },
          { title: '5. Checklist thẩm định', body: 'Trước khi đầu tư, cần xác nhận nền tảng có thể chứng minh traceability từ raw data đến evidence, MRV, value, asset, report và registry readiness.', cards: [['Traceability','Mọi kết quả có truy ngược về dữ liệu nguồn không?'],['Verification','Có workflow review và evidence package không?'],['Economics','Có hiển thị saving, revenue, payback và assumptions không?'],['Replication','Mô hình có mở rộng từ một khách hàng sang nhiều khách hàng không?']], quiz: 'Điểm chính: đầu tư vào proof có thể lặp lại, không phải demo một lần.' }
        ],
        finalTitle: 'Bạn đã hoàn thành khóa đầu tư thị trường carbon',
        finalBullets: ['Carbon asset cần bằng chứng và xác minh.', 'Giá trị tín chỉ phụ thuộc vào chất lượng, không chỉ số lượng.', 'AI MRV có thể là hạ tầng thị trường carbon.', 'Nhà đầu tư phải đánh giá data, methodology, regulatory và commercial risk.', 'Tín hiệu mạnh nhất là dữ liệu khách hàng thật có thể lặp lại.']
      },
      'zh-CN': {
        kicker: '投资者课程',
        title: '碳市场投资分析',
        sub: '碳正在成为新的资产市场。投资者需要理解项目质量、MRV 可信度、信用准备度、风险、定价和退出路径。',
        chapters: [
          { title: '1. 碳作为新的资产类别', body: '碳市场把经核证的减排转化为金融价值。投资者关注的不只是减少了多少 CO₂e，而是这些减排是否真实、具备额外性、可核证并可货币化。', cards: [['资产逻辑','经核证的减排可以成为碳资产候选或碳信用'],['市场类型','合规市场和自愿市场采用不同规则和价格'],['质量溢价','高质量 MRV 和可信方法学可以带来更高价值'],['投资视角','先评估数据完整性，再评估上行空间']], quiz: '重点：碳价值取决于证据，而不只是数量。' },
          { title: '2. 什么决定信用价值', body: '碳信用价值由方法学、额外性、持久性、泄漏风险、注册机构接受度、买方需求和 MRV 证据可信度共同决定。', cards: [['额外性','如果没有项目，减排是否会发生？'],['持久性','减排或移除效果能否持续？'],['泄漏','项目是否导致其他地方排放增加？'],['注册准备度','项目包能否满足核证和注册审查？']], quiz: '重点：大的 CO₂e 数字如果没有质量检查，价值很弱。' },
          { title: '3. MRV 平台投资逻辑', body: 'AI MRV 平台可能成为碳资产市场基础设施，因为它能收集数据、封存证据、计算减排并准备核证材料包。', cards: [['数据壁垒','运营数据形成可防守的洞察'],['信任层','哈希、签名、审计日志和校准记录降低操纵风险'],['可扩展性','配置驱动的方法学支持多行业和多国家'],['收入模式','SaaS、MRV 服务费、报告、核证支持和伙伴集成']], quiz: '重点：平台价值在于可信数据管道。' },
          { title: '4. 投资风险', body: '投资者必须区分真实碳基础设施和未经验证的声明。主要风险包括数据质量、方法学薄弱、监管变化、重复计算、项目执行和买方需求。', cards: [['数据风险','源数据缺失或被篡改会削弱资产质量'],['方法学风险','错误因子或过时方法会使估算失效'],['监管风险','规则会随国家和年份变化'],['商业风险','碳价值必须连接到真实付费客户或买方']], quiz: '重点：风险分析必须覆盖数据、方法、监管和收入。' },
          { title: '5. 投资尽调清单', body: '投资前应确认平台能否证明从原始数据到 evidence、MRV、value、asset、report 和 registry readiness 的完整可追溯性。', cards: [['可追溯性','每个结果能否追溯到源数据？'],['核证','是否有审核流程和证据包？'],['经济性','是否可见节省、收入、回收期和假设？'],['复制性','模式能否从一个客户扩展到多个客户？']], quiz: '重点：投资可复制的证明，而不是一次性演示。' }
        ],
        finalTitle: '你已完成碳市场投资者课程',
        finalBullets: ['碳资产需要证据和核证。', '信用价值取决于质量，不只是数量。', 'AI MRV 可以成为碳市场基础设施。', '投资者必须评估数据、方法、监管和商业风险。', '最强信号是真实且可复制的客户数据。']
      }
    },
    '06_government.html': {
      'en-US': {
        kicker: 'Government and Public Sector Course',
        title: 'National Carbon Policy Education',
        sub: 'Carbon neutrality is not only environmental policy. It is industrial strategy, regional competitiveness, infrastructure planning, and public trust.',
        chapters: [
          { title: '1. Carbon neutrality as industrial policy', body: 'Governments need carbon policy that creates measurable reductions, new industries, jobs, and investment. The center of this policy is reliable data.', cards: [['Public objective','Reduce emissions while protecting economic competitiveness.'],['Industrial transition','Support EV, solar, ESS, biogas, factories, and logistics.'],['Regional strategy','Cities and provinces can build carbon programs around local assets.'],['Data foundation','Policy impact must be measured and verified.']], quiz: 'Key point: carbon neutrality is also an economic and industrial policy.' },
          { title: '2. National MRV infrastructure', body: 'A public carbon program needs a trusted MRV system. Without MRV, the government cannot prove whether a policy, subsidy, or pilot actually reduced emissions.', cards: [['Measurement','Collect mobility, energy, solar, factory, and waste data.'],['Reporting','Aggregate reductions by project, region, industry, and year.'],['Verification','Use evidence, audit trails, calibration, and review workflows.'],['Transparency','Citizens and institutions need clear proof of results.']], quiz: 'Key point: public carbon policy needs proof, not only announcements.' },
          { title: '3. Regional carbon programs', body: 'Local governments can create programs by connecting fleets, charging operators, solar sites, factories, and public buildings into a verified carbon portfolio.', cards: [['EV mobility','Taxi, bus, logistics, and public fleet transition.'],['Renewable energy','Solar, ESS, charging, and demand management.'],['Industrial sites','Factory energy efficiency and process improvement.'],['Portfolio view','Track CO₂e, value, investment, progress, and risk by region.']], quiz: 'Key point: a city can operate carbon reduction as a portfolio.' },
          { title: '4. Public-private collaboration', body: 'Carbon transition requires cooperation among government, private operators, technology platforms, verifiers, financiers, and citizens. Each actor needs clear roles and evidence-based reporting.', cards: [['Government','Sets goals, standards, incentives, and public accountability.'],['Private operators','Provide real operational data and execute projects.'],['Verifiers','Review evidence and methodology.'],['Finance','Supports expansion when data proves performance.']], quiz: 'Key point: verified data connects policy, private execution, and finance.' },
          { title: '5. What public agencies should prepare', body: 'Before scaling, agencies should define data standards, partner onboarding, MRV methodology, reporting format, audit process, and privacy/security rules.', cards: [['Data standard','Common fields, units, source types, and timestamps.'],['Governance','Approval rights, review roles, and audit responsibilities.'],['Pilot design','Start with one proven customer or region, then replicate.'],['Public report','Show results in a format citizens and officials can understand.']], quiz: 'Key point: start with a measurable pilot and build a repeatable template.' }
        ],
        finalTitle: 'You completed the public-sector carbon policy course',
        finalBullets: ['Carbon neutrality is industrial and regional strategy.', 'MRV is public infrastructure for trusted climate policy.', 'Regional programs can combine mobility, energy, and industry.', 'Public-private collaboration needs evidence-based roles.', 'A verified pilot should become the replication template.']
      },
      'th-TH': {
        kicker: 'หลักสูตรภาครัฐและหน่วยงานสาธารณะ',
        title: 'นโยบายคาร์บอนนิวทรัลระดับประเทศ',
        sub: 'คาร์บอนนิวทรัลไม่ใช่แค่นโยบายสิ่งแวดล้อม แต่เป็นยุทธศาสตร์อุตสาหกรรม ความสามารถแข่งขันระดับพื้นที่ โครงสร้างพื้นฐาน และความเชื่อมั่นสาธารณะ',
        chapters: [
          { title: '1. คาร์บอนนิวทรัลในฐานะนโยบายอุตสาหกรรม', body: 'รัฐบาลต้องมีนโยบายคาร์บอนที่สร้างการลดที่วัดได้ อุตสาหกรรมใหม่ งาน และการลงทุน ศูนย์กลางของนโยบายนี้คือข้อมูลที่เชื่อถือได้', cards: [['เป้าหมายสาธารณะ','ลดการปล่อยพร้อมรักษาความสามารถแข่งขันเศรษฐกิจ'],['การเปลี่ยนอุตสาหกรรม','สนับสนุน EV, solar, ESS, biogas, factory และ logistics'],['ยุทธศาสตร์พื้นที่','เมืองและจังหวัดสร้าง program จากสินทรัพย์ท้องถิ่นได้'],['ฐานข้อมูล','ผลกระทบนโยบายต้องวัดและตรวจสอบได้']], quiz: 'ประเด็นสำคัญ: คาร์บอนนิวทรัลเป็นนโยบายเศรษฐกิจและอุตสาหกรรมด้วย' },
          { title: '2. โครงสร้างพื้นฐาน MRV ระดับชาติ', body: 'โครงการคาร์บอนภาครัฐต้องมี MRV ที่เชื่อถือได้ หากไม่มี MRV รัฐจะพิสูจน์ไม่ได้ว่านโยบาย เงินสนับสนุน หรือ pilot ลดการปล่อยจริงหรือไม่', cards: [['Measurement','เก็บข้อมูล mobility, energy, solar, factory และ waste'],['Reporting','รวมผลลดตาม project, region, industry และ year'],['Verification','ใช้ evidence, audit trail, calibration และ review workflow'],['Transparency','ประชาชนและหน่วยงานต้องเห็นหลักฐานผลลัพธ์ชัดเจน']], quiz: 'ประเด็นสำคัญ: นโยบายคาร์บอนสาธารณะต้องมี proof ไม่ใช่แค่ประกาศ' },
          { title: '3. Program คาร์บอนระดับพื้นที่', body: 'ท้องถิ่นสามารถสร้าง program โดยเชื่อม fleet, charging operator, solar site, factory และอาคารรัฐเป็น carbon portfolio ที่ตรวจสอบได้', cards: [['EV mobility','Taxi, bus, logistics และ public fleet transition'],['พลังงานหมุนเวียน','Solar, ESS, charging และ demand management'],['พื้นที่อุตสาหกรรม','ประสิทธิภาพพลังงานโรงงานและปรับปรุง process'],['Portfolio view','ติดตาม CO₂e, value, investment, progress และ risk ตามพื้นที่']], quiz: 'ประเด็นสำคัญ: เมืองสามารถบริหารการลดคาร์บอนเป็น portfolio ได้' },
          { title: '4. ความร่วมมือรัฐ-เอกชน', body: 'การเปลี่ยนผ่านคาร์บอนต้องร่วมมือระหว่างรัฐ ผู้ประกอบการ เทคโนโลยี verifier การเงิน และประชาชน ทุกฝ่ายต้องมีบทบาทชัดเจนและรายงานด้วยหลักฐาน', cards: [['ภาครัฐ','กำหนดเป้าหมาย มาตรฐาน incentive และความรับผิดชอบสาธารณะ'],['เอกชน','ให้ข้อมูลปฏิบัติการจริงและดำเนินโครงการ'],['Verifier','ตรวจ evidence และ methodology'],['Finance','สนับสนุนการขยายเมื่อข้อมูลพิสูจน์ performance']], quiz: 'ประเด็นสำคัญ: ข้อมูลที่ตรวจสอบแล้วเชื่อมนโยบาย การปฏิบัติ และเงินทุน' },
          { title: '5. สิ่งที่หน่วยงานควรเตรียม', body: 'ก่อนขยายผล หน่วยงานควรกำหนด data standard, partner onboarding, MRV methodology, report format, audit process และ privacy/security rules', cards: [['Data standard','Field, unit, source type และ timestamp ร่วมกัน'],['Governance','สิทธิอนุมัติ บทบาท review และ audit responsibility'],['Pilot design','เริ่มจากลูกค้าหรือพื้นที่ที่พิสูจน์แล้ว แล้วค่อย replicate'],['Public report','แสดงผลในรูปแบบที่ประชาชนและเจ้าหน้าที่เข้าใจได้']], quiz: 'ประเด็นสำคัญ: เริ่มจาก pilot ที่วัดได้และสร้าง template ที่ทำซ้ำได้' }
        ],
        finalTitle: 'คุณเรียนจบหลักสูตรนโยบายคาร์บอนภาครัฐแล้ว',
        finalBullets: ['คาร์บอนนิวทรัลคือยุทธศาสตร์อุตสาหกรรมและพื้นที่', 'MRV คือโครงสร้างพื้นฐานนโยบายภูมิอากาศที่เชื่อถือได้', 'Program ระดับพื้นที่รวม mobility, energy และ industry ได้', 'ความร่วมมือรัฐ-เอกชนต้องมีบทบาทบนหลักฐาน', 'Pilot ที่ตรวจสอบแล้วควรเป็น template สำหรับขยายผล']
      },
      'vi-VN': {
        kicker: 'Khóa học cho chính phủ và khu vực công',
        title: 'Đào tạo chính sách carbon quốc gia',
        sub: 'Trung hòa carbon không chỉ là chính sách môi trường. Đó là chiến lược công nghiệp, năng lực cạnh tranh địa phương, quy hoạch hạ tầng và niềm tin công chúng.',
        chapters: [
          { title: '1. Trung hòa carbon là chính sách công nghiệp', body: 'Chính phủ cần chính sách carbon tạo ra giảm phát thải đo được, ngành mới, việc làm và đầu tư. Trung tâm của chính sách này là dữ liệu đáng tin cậy.', cards: [['Mục tiêu công','Giảm phát thải đồng thời bảo vệ năng lực cạnh tranh kinh tế'],['Chuyển đổi công nghiệp','Hỗ trợ EV, solar, ESS, biogas, nhà máy và logistics'],['Chiến lược vùng','Thành phố và tỉnh có thể xây program carbon từ tài sản địa phương'],['Nền tảng dữ liệu','Tác động chính sách phải được đo và xác minh']], quiz: 'Điểm chính: trung hòa carbon cũng là chính sách kinh tế và công nghiệp.' },
          { title: '2. Hạ tầng MRV quốc gia', body: 'Chương trình carbon công cần hệ thống MRV đáng tin. Không có MRV, chính phủ không thể chứng minh chính sách, trợ cấp hoặc pilot có thật sự giảm phát thải hay không.', cards: [['Measurement','Thu thập dữ liệu mobility, energy, solar, factory và waste'],['Reporting','Tổng hợp giảm phát thải theo dự án, vùng, ngành và năm'],['Verification','Dùng evidence, audit trail, calibration và review workflow'],['Transparency','Người dân và cơ quan cần bằng chứng kết quả rõ ràng']], quiz: 'Điểm chính: chính sách carbon công cần bằng chứng, không chỉ thông báo.' },
          { title: '3. Chương trình carbon cấp vùng', body: 'Chính quyền địa phương có thể tạo program bằng cách kết nối fleet, charging operator, solar site, factory và tòa nhà công thành carbon portfolio đã xác minh.', cards: [['EV mobility','Chuyển đổi taxi, bus, logistics và đội xe công'],['Năng lượng tái tạo','Solar, ESS, charging và demand management'],['Khu công nghiệp','Hiệu quả năng lượng nhà máy và cải tiến quy trình'],['Portfolio view','Theo dõi CO₂e, value, investment, progress và risk theo vùng']], quiz: 'Điểm chính: một thành phố có thể vận hành giảm carbon như một portfolio.' },
          { title: '4. Hợp tác công tư', body: 'Chuyển đổi carbon cần hợp tác giữa chính phủ, doanh nghiệp vận hành, nền tảng công nghệ, verifier, tài chính và người dân. Mỗi bên cần vai trò rõ và báo cáo dựa trên bằng chứng.', cards: [['Chính phủ','Đặt mục tiêu, tiêu chuẩn, ưu đãi và trách nhiệm công'],['Doanh nghiệp','Cung cấp dữ liệu vận hành thật và triển khai dự án'],['Verifier','Rà soát evidence và methodology'],['Tài chính','Hỗ trợ mở rộng khi dữ liệu chứng minh hiệu quả']], quiz: 'Điểm chính: dữ liệu đã xác minh kết nối chính sách, thực thi tư nhân và tài chính.' },
          { title: '5. Cơ quan công cần chuẩn bị gì', body: 'Trước khi mở rộng, cơ quan cần xác định data standard, partner onboarding, MRV methodology, report format, audit process và privacy/security rules.', cards: [['Data standard','Field, unit, source type và timestamp chung'],['Governance','Quyền phê duyệt, vai trò review và trách nhiệm audit'],['Pilot design','Bắt đầu với một khách hàng hoặc vùng đã chứng minh rồi nhân rộng'],['Public report','Hiển thị kết quả theo cách người dân và cán bộ hiểu được']], quiz: 'Điểm chính: bắt đầu bằng pilot đo được và xây template lặp lại được.' }
        ],
        finalTitle: 'Bạn đã hoàn thành khóa chính sách carbon khu vực công',
        finalBullets: ['Trung hòa carbon là chiến lược công nghiệp và vùng.', 'MRV là hạ tầng công cho chính sách khí hậu đáng tin.', 'Program cấp vùng có thể kết hợp mobility, energy và industry.', 'Hợp tác công tư cần vai trò dựa trên bằng chứng.', 'Pilot đã xác minh nên trở thành template nhân rộng.']
      },
      'zh-CN': {
        kicker: '政府与公共机构课程',
        title: '国家碳中和政策教育',
        sub: '碳中和不只是环境政策，也是产业战略、区域竞争力、基础设施规划和公共信任。',
        chapters: [
          { title: '1. 碳中和作为产业政策', body: '政府需要能够创造可测量减排、新产业、就业和投资的碳政策。这类政策的核心是可信数据。', cards: [['公共目标','在保护经济竞争力的同时减少排放'],['产业转型','支持 EV、太阳能、ESS、沼气、工厂和物流'],['区域战略','城市和省份可以围绕本地资产建立碳项目群'],['数据基础','政策效果必须被测量和核证']], quiz: '重点：碳中和也是经济和产业政策。' },
          { title: '2. 国家 MRV 基础设施', body: '公共碳项目需要可信 MRV 系统。没有 MRV，政府无法证明政策、补贴或试点是否真正减少了排放。', cards: [['测量','收集交通、能源、太阳能、工厂和废弃物数据'],['报告','按项目、区域、行业和年份汇总减排'],['核证','使用证据、审计轨迹、校准和审核流程'],['透明度','公众和机构需要清楚的结果证明']], quiz: '重点：公共碳政策需要证明，而不只是公告。' },
          { title: '3. 区域碳项目群', body: '地方政府可以把车队、充电运营商、太阳能站点、工厂和公共建筑连接成经核证的碳资产组合。', cards: [['电动出行','出租车、公交、物流和公共车队转型'],['可再生能源','太阳能、ESS、充电和需求管理'],['工业场景','工厂能效和工艺改进'],['组合视图','按区域追踪 CO₂e、价值、投资、进度和风险']], quiz: '重点：城市可以像管理组合一样运营减碳。' },
          { title: '4. 公私协作', body: '碳转型需要政府、民营运营方、技术平台、核证方、金融机构和公众合作。每个角色都需要清晰职责和基于证据的报告。', cards: [['政府','设定目标、标准、激励和公共问责'],['民营运营方','提供真实运营数据并执行项目'],['核证方','审核证据和方法学'],['金融','当数据证明绩效后支持扩张']], quiz: '重点：经核证数据连接政策、民间执行和资金。' },
          { title: '5. 公共机构应准备什么', body: '在规模化之前，机构应定义数据标准、伙伴接入、MRV 方法学、报告格式、审计流程和隐私安全规则。', cards: [['数据标准','统一字段、单位、来源类型和时间戳'],['治理','审批权限、审核角色和审计责任'],['试点设计','从一个已验证客户或区域开始，然后复制'],['公共报告','用公众和公务人员都能理解的格式展示结果']], quiz: '重点：从可测量试点开始，建立可复制模板。' }
        ],
        finalTitle: '你已完成公共部门碳政策课程',
        finalBullets: ['碳中和是产业和区域战略。', 'MRV 是可信气候政策的公共基础设施。', '区域项目群可以结合出行、能源和工业。', '公私协作需要基于证据的角色分工。', '经验证试点应成为复制模板。']
      }
    }
  };

  function pageKey() {
    const last = location.pathname.split('/').pop() || 'index.html';
    return COURSE_DATA[last] ? last : 'index.html';
  }

  function currentLang() {
    const saved = localStorage.getItem(STORAGE_KEY) || localStorage.getItem('zenovLanguage');
    return LANGUAGES[saved] ? saved : DEFAULT_LANG;
  }

  function languageBundle(lang) {
    const page = COURSE_DATA[pageKey()] || COURSE_DATA['index.html'];
    return page[lang] || page[DEFAULT_LANG];
  }

  function ensureToolbar() {
    if (document.querySelector('.zenov-edu-language')) return;
    const wrap = document.createElement('div');
    wrap.className = 'zenov-edu-language';
    wrap.innerHTML = `
      <label for="zenovEduLanguage">${LANGUAGES[DEFAULT_LANG].ui.language}</label>
      <select id="zenovEduLanguage" aria-label="Education language">
        ${Object.entries(LANGUAGES).map(([code, item]) => `<option value="${code}">${item.label}</option>`).join('')}
      </select>
    `;
    document.body.appendChild(wrap);

    const status = document.createElement('div');
    status.className = 'zenov-edu-translate-status';
    status.id = 'zenovEduTranslateStatus';
    document.body.appendChild(status);

    const panel = document.createElement('section');
    panel.className = 'zenov-edu-local-summary';
    panel.id = 'zenovEduLocalSummary';
    document.body.insertBefore(panel, document.body.firstElementChild);

    const select = document.getElementById('zenovEduLanguage');
    select.value = currentLang();
    select.addEventListener('change', () => setLanguage(select.value));
  }

  function setText(selector, value) {
    if (!value) return;
    document.querySelectorAll(selector).forEach((node) => {
      node.textContent = value;
    });
  }

  function setHero(selector, value) {
    if (!value) return;
    document.querySelectorAll(selector).forEach((node) => {
      node.textContent = value;
    });
  }

  function translateCards(data) {
    if (!data.cards) return;
    const cards = document.querySelectorAll('.edu-card .card-title, .grid .card .value');
    cards.forEach((node, index) => {
      if (data.cards[index]) node.textContent = data.cards[index];
    });
  }

  function translateButtons(lang) {
    const ui = LANGUAGES[lang].ui;
    document.querySelectorAll('.btn-start').forEach((button) => button.textContent = ui.start);
    document.querySelectorAll('.btn-next').forEach((button) => {
      const raw = button.textContent;
      if (/수료|완료|Complete|จบ|完成|Hoàn/.test(raw)) button.textContent = ui.done;
      else button.textContent = ui.next;
    });
    document.querySelectorAll('.btn-back').forEach((button) => {
      if (/목록|List|รายการ|列表|Danh/.test(button.textContent)) button.textContent = ui.list;
      else button.textContent = ui.prev;
    });
    document.querySelectorAll('.btn-restart').forEach((button) => button.textContent = ui.restart);
  }

  function updateSummary(lang, data) {
    const panel = document.getElementById('zenovEduLocalSummary');
    if (!panel) return;
    const ui = LANGUAGES[lang].ui;
    panel.innerHTML = `
      <div class="zenov-edu-summary-kicker">${ui.summary}</div>
      <h2>${data.title}</h2>
      <p>${data.sub}</p>
      <ul>${(data.bullets || []).map((item) => `<li>${item}</li>`).join('')}</ul>
    `;
  }

  function htmlEscape(value) {
    return String(value ?? '')
      .replaceAll('&', '&amp;')
      .replaceAll('<', '&lt;')
      .replaceAll('>', '&gt;')
      .replaceAll('"', '&quot;')
      .replaceAll("'", '&#39;');
  }

  function fullCourseBundle(lang) {
    const page = FULL_COURSE_DATA[pageKey()];
    if (!page || lang === DEFAULT_LANG) return null;
    return page[lang] || null;
  }

  function ensureTranslatedCourseContainer() {
    let container = document.getElementById('zenovTranslatedCourse');
    if (container) return container;
    container = document.createElement('main');
    container.id = 'zenovTranslatedCourse';
    container.className = 'zenov-translated-course';
    document.body.appendChild(container);
    return container;
  }

  function renderTranslatedCourse(lang) {
    const data = fullCourseBundle(lang);
    const container = ensureTranslatedCourseContainer();
    if (!data) {
      document.body.classList.remove('zenov-translated-mode');
      container.innerHTML = '';
      return;
    }

    document.body.classList.add('zenov-translated-mode');
    const chapters = (data.chapters || []).map((chapter) => {
      const cards = (chapter.cards || []).map(([title, body]) => `
        <article class="zenov-course-card">
          <strong>${htmlEscape(title)}</strong>
          <p>${htmlEscape(body)}</p>
        </article>
      `).join('');

      return `
        <section class="zenov-course-section">
          <h2>${htmlEscape(chapter.title)}</h2>
          <p>${htmlEscape(chapter.body)}</p>
          ${cards ? `<div class="zenov-course-grid">${cards}</div>` : ''}
          ${chapter.quiz ? `<div class="zenov-course-quiz">${htmlEscape(chapter.quiz)}</div>` : ''}
        </section>
      `;
    }).join('');

    const finalBullets = (data.finalBullets || []).map((item) => `<li>${htmlEscape(item)}</li>`).join('');

    container.innerHTML = `
      <section class="zenov-course-hero">
        <div class="zenov-course-kicker">${htmlEscape(data.kicker)}</div>
        <h1>${htmlEscape(data.title)}</h1>
        <p>${htmlEscape(data.sub)}</p>
      </section>
      ${chapters}
      <section class="zenov-course-final">
        <h2>${htmlEscape(data.finalTitle)}</h2>
        <ul>${finalBullets}</ul>
      </section>
    `;
  }

  function setLanguage(lang) {
    if (!LANGUAGES[lang]) lang = DEFAULT_LANG;
    localStorage.setItem(STORAGE_KEY, lang);
    localStorage.setItem('zenovLanguage', lang);
    const meta = LANGUAGES[lang];
    const data = languageBundle(lang);

    document.documentElement.lang = meta.html;
    document.title = data.title || document.title;

    const select = document.getElementById('zenovEduLanguage');
    if (select) select.value = lang;
    setText('.zenov-edu-language label', meta.ui.language);
    setText('#zenovEduTranslateStatus', meta.ui.original);
    setText('.zenov-platform-return', meta.back);
    document.querySelectorAll('.zenov-platform-return').forEach((link) => {
      link.setAttribute('href', '/education.html?v=165');
    });

    setHero('.hero-title', data.hero || data.title);
    setText('.hero-sub', data.sub);
    setText('.hero-eyebrow', data.title);
    setText('.hero-tag', data.title);
    translateCards(data);
    translateButtons(lang);
    updateSummary(lang, data);
    renderTranslatedCourse(lang);
  }

  document.addEventListener('DOMContentLoaded', () => {
    ensureToolbar();
    setLanguage(currentLang());
  });
})();
