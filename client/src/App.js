import React, { useState } from 'react';
import './App.css';

function Header() {
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  const scrollToSection = (sectionId) => {
    const element = document.getElementById(sectionId);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
    setIsMenuOpen(false);
  };

  return (
    <header className="header">
      <div className="header-container">
        <div className="logo">
          <img src="https://static.tildacdn.com/tild3462-3130-4964-a465-653362663166/38.png" alt="СОК" />
          <span>СОК</span>
        </div>
        <button 
          className="mobile-menu-btn"
          onClick={() => setIsMenuOpen(!isMenuOpen)}
        >
          ☰
        </button>
        <nav className={`nav ${isMenuOpen ? 'nav-open' : ''}`}>
          <a onClick={() => scrollToSection('about')}>О ПРОЕКТЕ</a>
          <a onClick={() => scrollToSection('directions')}>НАПРАВЛЕНИЯ</a>
          <a onClick={() => scrollToSection('schedule')}>РАСПИСАНИЕ</a>
          <a onClick={() => scrollToSection('stages')}>ЭТАПЫ</a>
          <a onClick={() => scrollToSection('apply')}>ПОДАТЬ ЗАЯВКУ</a>
          <a onClick={() => scrollToSection('questions')}>СОМНЕНИЯ?</a>
          <a onClick={() => scrollToSection('contacts')}>КОНТАКТЫ</a>
        </nav>
      </div>
    </header>
  );
}

function Hero() {
  return (
    <section className="hero">
      <div className="hero-content">
        <h1>СОК - Синергия. Опыт. Креатив.</h1>
        <p className="hero-subtitle">
          конкурс, где бизнес получает решения и доступ к молодым специалистам, 
          а студенты разрабатывают продукт для компании
        </p>
      </div>
    </section>
  );
}

function About() {
  return (
    <section id="about" className="section about">
      <div className="container">
        <h2>О ПРОЕКТЕ</h2>
        <div className="about-grid">
          <div className="about-card">
            <img src="https://thb.tildacdn.com/tild6533-3533-4831-b964-663961653238/-/resize/20x/37.png" alt="Опыт" />
            <h3>ОПЫТ</h3>
            <p>
              Вы сформируете навык работы с новым поколением Зуммеров, которых все больше 
              на рынке, а так же поспособствуете развитию навыков у ваших сотрудников 
              при включении их в команду проекта
            </p>
          </div>
          <div className="about-card">
            <img src="https://thb.tildacdn.com/tild6533-3533-4831-b964-663961653238/-/resize/20x/37.png" alt="Кадры" />
            <h3>КАДРЫ</h3>
            <p>
              Вы сотрудничаете с будущими специалистами, а это лучшее резюме, которое 
              позволит выбрать того, кто уже доказал свои навыки на вашем проекте и 
              адаптировался к работе с вашей компанией
            </p>
          </div>
          <div className="about-card">
            <img src="https://thb.tildacdn.com/tild6533-3533-4831-b964-663961653238/-/resize/20x/37.png" alt="Синергия" />
            <h3>СИНЕРГИЯ</h3>
            <p>
              Cada участник получает результат: Бизнес - продукт, кадры, администрирование 
              и поддержка в разработке продукта. Студент - опыт, связи, закрытие практики 
              и призы. Учебное заведение - расширение базы компаний
            </p>
          </div>
          <div className="about-card">
            <img src="https://thb.tildacdn.com/tild6533-3533-4831-b964-663961653238/-/resize/20x/37.png" alt="Продукт" />
            <h3>ПРОДУКТ</h3>
            <p>
              Вы приобретаете необходимый в жизни бизнеса инструмент готовый к работе. 
              Например: Сайт, приложение, бренд бук, дизайн упаковки, пакет для рекрутинга, 
              пакет для адаптации, smm-продвижение и многое другое
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}

function Directions() {
  const directions = [
    {
      title: 'Брендинг и ребрендинг компаний',
      subtitle: 'Упаковка продукта: физическая и цифровая',
      image: 'https://thb.tildacdn.com/tild6331-3966-4566-b662-646134323861/-/resize/20x/_6.png',
      link: '#'
    },
    {
      title: 'Создание сайтов, лендингов',
      subtitle: 'Разработка приложений',
      image: 'https://thb.tildacdn.com/tild3064-6232-4566-b830-396131333861/-/resize/20x/_6_.png',
      link: '#'
    },
    {
      title: 'Разработка и оформление "Пакета для рекрутинга"',
      subtitle: 'Создание инструментов адаптации - "Welcome book"',
      image: 'https://thb.tildacdn.com/tild3336-3833-4761-b866-373735656638/-/resize/20x/hr_6_.png',
      link: '#'
    },
    {
      title: 'Ведение и оформление социальных сетей',
      subtitle: 'SMM стратегия',
      image: 'https://thb.tildacdn.com/tild6663-3361-4963-b030-366233363334/-/resize/20x/smm_7.png',
      link: '#'
    }
  ];

  return (
    <section id="directions" className="section directions">
      <div className="container">
        <h2>НАПРАВЛЕНИЯ</h2>
        <div className="directions-grid">
          {directions.map((dir, index) => (
            <div key={index} className="direction-card">
              <img src={dir.image} alt={dir.title} />
              <div className="direction-content">
                <h3>{dir.title}</h3>
                <p>{dir.subtitle}</p>
                <a href={dir.link} className="direction-link">ХОЧУ</a>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

function Schedule() {
  return (
    <section id="schedule" className="section schedule">
      <div className="container">
        <h2>РАСПИСАНИЕ</h2>
        <div className="schedule-grid">
          <div className="schedule-card">
            <div className="schedule-month">февраль</div>
            <div className="schedule-icon">📅</div>
            <h3>ИДУ!</h3>
            <p>на 2026 г.</p>
          </div>
          <div className="schedule-card">
            <div className="schedule-month">февраль</div>
            <div className="schedule-icon">📅</div>
          </div>
          <div className="schedule-card">
            <div className="schedule-month">февраль</div>
            <div className="schedule-icon">📅</div>
          </div>
          <div className="schedule-card">
            <div className="schedule-month">февраль</div>
            <div className="schedule-icon">📅</div>
          </div>
        </div>
      </div>
    </section>
  );
}

function Stages() {
  const stages = [
    {
      title: 'СТАРТ',
      description: 'встреча знакомства, где компании рассказывают о себе и происходит распределение между командами',
      icon: 'https://thb.tildacdn.com/tild3961-3531-4163-b436-313136653664/-/resize/20x/34.png'
    },
    {
      title: 'РАБОТА НАД ПРОЕКТОМ',
      description: 'онлайн встречи команд и представителей компании, защита контрольных точек командами',
      icon: 'https://thb.tildacdn.com/tild3961-3531-4163-b436-313136653664/-/resize/20x/34.png'
    },
    {
      title: 'ЗАЩИТА ПРОЕКТОВ',
      description: 'команды подготавливают и сдают презентации работ',
      icon: 'https://thb.tildacdn.com/tild3961-3531-4163-b436-313136653664/-/resize/20x/34.png'
    },
    {
      title: 'НАГРАЖДЕНИЕ',
      description: 'торжественная церемония вручения призов победителям',
      icon: 'https://thb.tildacdn.com/tild3961-3531-4163-b436-313136653664/-/resize/20x/34.png'
    }
  ];

  return (
    <section id="stages" className="section stages">
      <div className="container">
        <h2>ЭТАПЫ</h2>
        <div className="stages-grid">
          {stages.map((stage, index) => (
            <div key={index} className="stage-card">
              <img src={stage.icon} alt={stage.title} />
              <h3>{stage.title}</h3>
              <p>{stage.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

function ApplyForm() {
  const [formData, setFormData] = useState({
    fullName: '',
    phone: '',
    option: ''
  });
  const [submitted, setSubmitted] = useState(false);
  const [error, setError] = useState('');

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (!formData.fullName || !formData.phone || !formData.option) {
      setError('Заполните все поля');
      return;
    }

    try {
      const response = await fetch('http://localhost:8080/api/applications', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
      });

      if (response.ok) {
        setSubmitted(true);
        setFormData({ fullName: '', phone: '', option: '' });
      } else {
        setError('Ошибка при отправке заявки');
      }
    } catch (err) {
      setError('Ошибка соединения с сервером');
    }
  };

  if (submitted) {
    return (
      <section id="apply" className="section apply">
        <div className="container">
          <div className="success-message">
            <img src="https://thb.tildacdn.com/tild3865-6535-4634-b662-386533316532/-/resize/20x/30.png" alt="✓" />
            <h2>Данные успешно отправлены. Спасибо!</h2>
            <p>Мы вам обязательно перезвоним</p>
          </div>
        </div>
      </section>
    );
  }

  return (
    <section id="apply" className="section apply" style={{ paddingTop: '45px', paddingBottom: '30px' }}>
      <div className="container">
        <div className="apply-form-wrapper">
          <div className="apply-title" style={{ fontSize: '72px', marginBottom: '75px', fontFamily: 'Montserrat', fontWeight: '600', textTransform: 'uppercase', color: '#000' }}>
            ПОДАТЬ ЗАЯВКУ
          </div>
          
          <div className="t-form__descr" style={{ maxWidth: '560px', marginBottom: '30px' }}>
            Оставьте ваш телефон и мы вам обязательно позвоним
          </div>

          <form id="form1236046861" name="form1236046861" role="form" onSubmit={handleSubmit} className="t-form js-form-proccess t-form_inputs-total_3">
            <div className="error-message-box" style={{ display: error ? 'block' : 'none' }}>
              <ul className="t-form__errorbox-text">
                {error && <li>{error}</li>}
              </ul>
            </div>

            <div className="t-form__inputsbox" style={{ marginBottom: '20px' }}>
              {/* ФИО */}
              <div className="t-input-group t-input-group_nm" style={{ marginBottom: '20px' }}>
                <div className="t-input-block" style={{ border: '1px solid #3f17d2', borderRadius: '15px' }}>
                  <input
                    type="text"
                    name="fullName"
                    id="input_fullName"
                    className="t-input js-tilda-rule"
                    value={formData.fullName}
                    onChange={handleChange}
                    placeholder="ФИО"
                    style={{ color: '#2d20d4', padding: '18px 20px', border: 'none', outline: 'none', width: '100%', borderRadius: '15px', fontFamily: 'Montserrat' }}
                  />
                </div>
              </div>

              {/* Телефон */}
              <div className="t-input-group t-input-group_ph" style={{ marginBottom: '20px' }}>
                <div className="t-input-block" style={{ border: '1px solid #3f17d2', borderRadius: '15px' }}>
                  <input
                    type="tel"
                    name="phone"
                    id="input_phone"
                    className="t-input js-tilda-rule"
                    value={formData.phone}
                    onChange={handleChange}
                    placeholder="+7(000)000-0000"
                    style={{ color: '#2d20d4', padding: '18px 20px', border: 'none', outline: 'none', width: '100%', borderRadius: '15px', fontFamily: 'Montserrat' }}
                  />
                </div>
              </div>

              {/* Выбор направления */}
              <div className="t-input-group t-input-group_sb" style={{ marginBottom: '30px' }}>
                <div className="t-input-block" style={{ border: '1px solid #3f17d2', borderRadius: '15px' }}>
                  <div className="t-select__wrapper">
                    <select
                      name="option"
                      id="input_option"
                      className="t-select js-tilda-rule"
                      value={formData.option}
                      onChange={handleChange}
                      style={{ color: formData.option ? '#2d20d4' : '#999', padding: '18px 20px', border: 'none', outline: 'none', width: '100%', borderRadius: '15px', fontFamily: 'Montserrat', cursor: 'pointer' }}
                    >
                      <option value="" style={{ color: '#2d20d4' }}>Выберите вариант из списка</option>
                      <option value="Хочу новый дизайн" style={{ color: '#2d20d4' }}>Хочу новый дизайн</option>
                      <option value="Хочу новый сайт" style={{ color: '#2d20d4' }}>Хочу новый сайт</option>
                      <option value="Хочу крутой найм" style={{ color: '#2d20d4' }}>Хочу крутой найм</option>
                      <option value="Хочу SMM стратегию" style={{ color: '#2d20d4' }}>Хочу SMM стратегию</option>
                    </select>
                  </div>
                </div>
              </div>
            </div>

            <div className="t-form__submit">
              <button type="submit" className="t-submit t-btnflex t-btnflex_type_submit t-btnflex_md" style={{
                display: 'inline-flex',
                alignItems: 'center',
                justifyContent: 'center',
                padding: '18px 40px',
                color: '#ffffff',
                backgroundImage: 'linear-gradient(0.287turn, rgba(35,248,244,1) 0%, rgba(44,113,212,1) 58%, rgba(58,83,209,1) 100%)',
                border: '2px solid #6389d8',
                borderRadius: '15px',
                fontFamily: 'Montserrat',
                fontWeight: '600',
                textTransform: 'uppercase',
                cursor: 'pointer',
                transition: 'all 0.2s ease-in-out',
                position: 'relative',
                overflow: 'hidden',
                zIndex: 1,
                width: '100%'
              }}
              onMouseOver={(e) => {
                e.currentTarget.style.setProperty('--hover-bg', '#4480e2');
              }}
              >
                <span className="t-btnflex__text">УЧАСТВУЮ</span>
              </button>
            </div>
          </form>

          <div className="t-form__bottom-text t-text t-text_xs" style={{ marginTop: '20px', fontSize: '14px', lineHeight: '1.5' }}>
            <div style={{ fontFamily: 'Montserrat' }}>
              <em style={{ color: 'rgb(0, 0, 0)', fontStyle: 'italic' }}>
                «Нажимая на кнопку "УЧАСТВУЮ", вы даете согласие на обработку персональных данных и подтверждаете ознакомление с
              </em>
              <br />
              <em style={{ color: 'rgb(0, 0, 0)', fontStyle: 'italic' }}>
                Политикой защиты персональных данных Ассоциации развития бизнеса и учебных заведений АРБУЗ.
              </em>
              <br />
              <strong style={{ fontFamily: 'Montserrat', color: 'rgb(115, 115, 115)' }}>
                <a href="https://disk.yandex.ru/i/cRKTINmZBVEpog" target="_blank" rel="noreferrer noopener" style={{ color: 'rgb(115, 115, 115)', textDecoration: 'underline' }}>
                  ПОЛИТИКА ЗАЩИТЫ И ОБРАБОТКИ ПЕРСОНАЛЬНЫХ ДАННЫХ КЛИЕНТОВ, КОНТРАГЕНТОВ И ПОЛЬЗОВАТЕЛЕ САЙТОВ
                </a>
              </strong>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

function Questions() {
  const questions = [
    {
      q: 'У меня нет на это времени и у моих сотрудников тоже',
      a: 'Роль не в ежедневном менторстве, а в постановке четкого ТЗ и выделении нескольких часов на ключевые этапы. Вся работа контролируется Ассоциацией АРБУЗ.'
    },
    {
      q: 'Студенты ничего не понимают в нашем бизнесе/нише. Что они могут предложить?',
      a: 'Работы студентов показывают их свежий взгляд, желание разобраться и увидеть индивидуальность вашей компании, что позволяет создавать креативно.'
    },
    {
      q: 'И что я получу в итоге? Красивый презентационный концепт, который нельзя использовать?',
      a: 'Задача команд разработать продукт готовый к работе. 90% участников-компаний прошлых конкурсов взяли в работу результаты команд.'
    },
    {
      q: 'А если результат будет плохой? Я просто зря потрачу время',
      a: 'Для бизнеса это возможность протестировать гипотезу на минимальные деньги. У вас будет вся информация для дальнейшей разработки.'
    },
    {
      q: 'Почему я должен за это платить?',
      a: 'Стоимость работы студентов несоизмеримо ниже рыночной. Деньги идут на организацию и призы, а не гонорар организаторам.'
    },
    {
      q: 'Мне это не нужно. У меня и так все работает',
      a: 'Участие в конкурсе — это история для соцсетей о социальной ответственности. Улучшение имиджа компании.'
    }
  ];

  return (
    <section id="questions" className="section questions">
      <div className="container">
        <h2>СОМНЕНИЯ?</h2>
        <div className="questions-grid">
          {questions.map((item, index) => (
            <div key={index} className="question-card">
              <h3>{item.q}</h3>
              <p>{item.a}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

function Footer() {
  return (
    <footer id="contacts" className="footer">
      <div className="container">
        <div className="footer-cta">
          <h2>«Мы ждём вашего хода.</h2>
          <h3>Готовы создать нечто уникальное?</h3>
          <p>Пришло время построить удивительное вместе!</p>
        </div>
        <div className="footer-content">
          <div className="footer-links">
            <a onClick={() => document.getElementById('stages').scrollIntoView({behavior:'smooth'})}>ЭТАПЫ</a>
            <a onClick={() => document.getElementById('contacts').scrollIntoView({behavior:'smooth'})}>КОНТАКТЫ</a>
            <a onClick={() => document.getElementById('apply').scrollIntoView({behavior:'smooth'})}>ПОДАТЬ ЗАЯВКУ</a>
            <a onClick={() => document.getElementById('about').scrollIntoView({behavior:'smooth'})}>О ПРОЕКТЕ</a>
            <a onClick={() => document.getElementById('directions').scrollIntoView({behavior:'smooth'})}>НАПРАВЛЕНИЯ</a>
            <a onClick={() => document.getElementById('schedule').scrollIntoView({behavior:'smooth'})}>РАСПИСАНИЕ</a>
          </div>
          <div className="footer-contact">
            <p><strong>ТЕЛЕФОН</strong> <a href="tel:+79221699555">+7 922 22 123 98</a></p>
            <p>© 2025 Ассоциация АРБУЗ</p>
            <div className="social-links">
              <a href="https://vk.com/associationarbuz?from=groups" target="_blank" rel="noopener noreferrer">
                <img src="https://thb.tildacdn.com/tild6262-3339-4530-b039-656632356432/-/resize/20x/free-icon-vkontakte-.png" alt="VK" />
              </a>
              <a href="https://t.me/arbuz_nko" target="_blank" rel="noopener noreferrer">
                <img src="https://thb.tildacdn.com/tild6161-3739-4166-b339-376133376162/-/resize/20x/free-icon-telegram-2.png" alt="Telegram" />
              </a>
              <a href="mailto:mail@nash-arbuz.ru">
                <img src="https://thb.tildacdn.com/tild6130-6665-4561-b266-303132653162/-/resize/20x/free-icon-connection.png" alt="Email" />
              </a>
            </div>
            <p className="footer-site">
              Сайт АРБУЗа <img src="https://static.tildacdn.com/img/tildacopy.png" alt="Tilda" />
            </p>
          </div>
        </div>
      </div>
    </footer>
  );
}

function App() {
  return (
    <div className="App">
      <Header />
      <main>
        <Hero />
        <About />
        <Directions />
        <Schedule />
        <Stages />
        <ApplyForm />
        <Questions />
      </main>
      <Footer />
    </div>
  );
}

export default App;
