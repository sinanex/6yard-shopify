/**
 * 6YARD STORE — Interactive Component Behaviors
 * - 3D Coverflow Layered Carousel
 * - Dynamic Delivery Countdown
 * - Size Guide Modal Toggle
 */

document.addEventListener('DOMContentLoaded', () => {
  initCoverflow();
  initDeliveryTimeline();
  initSizeGuideModal();
});

/* ==========================================================================
   1. 3D COVERFLOW CAROUSEL
   ========================================================================== */
function initCoverflow() {
  const container = document.querySelector('.coverflow-container');
  if (!container) return;

  const stage = container.querySelector('.coverflow-stage');
  const slides = Array.from(stage.querySelectorAll('.coverflow-slide'));
  const prevBtn = container.querySelector('.coverflow-arrow.prev-btn');
  const nextBtn = container.querySelector('.coverflow-arrow.next-btn');

  if (slides.length === 0) return;

  let activeIndex = 0;
  let autoplayTimer = null;
  let isPaused = false;
  let touchStartX = null;

  function updateSlides() {
    slides.forEach((slide, idx) => {
      slide.classList.remove('active', 'prev', 'next', 'hidden-slide');

      if (idx === activeIndex) {
        slide.classList.add('active');
      } else if (idx === (activeIndex - 1 + slides.length) % slides.length) {
        slide.classList.add('prev');
      } else if (idx === (activeIndex + 1) % slides.length) {
        slide.classList.add('next');
      } else {
        slide.classList.add('hidden-slide');
      }
    });
  }

  function nextSlide() {
    activeIndex = (activeIndex + 1) % slides.length;
    updateSlides();
  }

  function prevSlide() {
    activeIndex = (activeIndex - 1 + slides.length) % slides.length;
    updateSlides();
  }

  function startAutoplay() {
    if (slides.length <= 1) return;
    stopAutoplay();
    autoplayTimer = setInterval(() => {
      if (!isPaused) nextSlide();
    }, 4500);
  }

  function stopAutoplay() {
    if (autoplayTimer) {
      clearInterval(autoplayTimer);
      autoplayTimer = null;
    }
  }

  if (nextBtn) nextBtn.addEventListener('click', () => { nextSlide(); startAutoplay(); });
  if (prevBtn) prevBtn.addEventListener('click', () => { prevSlide(); startAutoplay(); });

  // Slide direct click navigation
  slides.forEach((slide, idx) => {
    slide.addEventListener('click', (e) => {
      if (slide.classList.contains('prev')) {
        e.preventDefault();
        prevSlide();
        startAutoplay();
      } else if (slide.classList.contains('next')) {
        e.preventDefault();
        nextSlide();
        startAutoplay();
      }
    });
  });

  // Hover pause
  container.addEventListener('mouseenter', () => { isPaused = true; });
  container.addEventListener('mouseleave', () => { isPaused = false; });

  // Touch Swipe
  container.addEventListener('touchstart', (e) => {
    touchStartX = e.touches[0].clientX;
  }, { passive: true });

  container.addEventListener('touchend', (e) => {
    if (touchStartX === null) return;
    const diff = touchStartX - e.changedTouches[0].clientX;
    if (Math.abs(diff) > 40) {
      if (diff > 0) nextSlide();
      else prevSlide();
      startAutoplay();
    }
    touchStartX = null;
  });

  updateSlides();
  startAutoplay();
}

/* ==========================================================================
   2. DYNAMIC DELIVERY TIMELINE
   ========================================================================== */
function initDeliveryTimeline() {
  const dtBox = document.querySelector('.delivery-timeline-box');
  if (!dtBox) return;

  const countdownEl = dtBox.querySelector('.dt-countdown-time');
  const dateRangeEl = dtBox.querySelector('.dt-delivery-range');
  const d1El = dtBox.querySelector('.dt-date-delivered-start');
  const d2El = dtBox.querySelector('.dt-date-delivered-end');
  const processEl = dtBox.querySelector('.dt-date-processing');

  const minProcessing = parseInt(dtBox.dataset.minProcessing || '2', 10);
  const maxProcessing = parseInt(dtBox.dataset.maxProcessing || '4', 10);
  const minDelivery = parseInt(dtBox.dataset.minDelivery || '5', 10);
  const maxDelivery = parseInt(dtBox.dataset.maxDelivery || '7', 10);

  function calculateDates() {
    const now = new Date();
    const endOfDay = new Date(now);
    endOfDay.setHours(23, 59, 59, 999);
    const diffMs = endOfDay.getTime() - now.getTime();
    const hrs = Math.floor(diffMs / (1000 * 60 * 60));
    const mins = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60));

    if (countdownEl) {
      countdownEl.textContent = `${hrs} h ${mins} min`;
    }

    const processMinD = new Date(); processMinD.setDate(processMinD.getDate() + minProcessing);
    const processMaxD = new Date(); processMaxD.setDate(processMaxD.getDate() + maxProcessing);

    const d1 = new Date(); d1.setDate(d1.getDate() + minProcessing + minDelivery);
    const d2 = new Date(); d2.setDate(d2.getDate() + maxProcessing + maxDelivery);

    const formatFull = (d) => d.toLocaleDateString('en-GB', { day: '2-digit', month: '2-digit', year: 'numeric' });
    const formatShort = (d) => d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });

    if (dateRangeEl) {
      dateRangeEl.textContent = `${formatFull(d1)} - ${formatFull(d2)}`;
    }
    if (processEl) {
      processEl.textContent = `${formatShort(processMinD)} - ${formatShort(processMaxD).split(' ')[1]}`;
    }
    if (d1El && d2El) {
      d1El.textContent = `${formatShort(d1)} - ${formatShort(d2).split(' ')[1]}`;
    }
  }

  calculateDates();
  setInterval(calculateDates, 60000);
}

/* ==========================================================================
   3. SIZE GUIDE MODAL
   ========================================================================== */
function initSizeGuideModal() {
  const triggers = document.querySelectorAll('[data-open-size-guide]');
  const modal = document.getElementById('SizeGuideModal');
  if (!modal || triggers.length === 0) return;

  const closeBtn = modal.querySelector('[data-close-size-guide]');
  const backdrop = modal.querySelector('.modal-backdrop');

  function openModal() {
    modal.classList.add('is-open');
    document.body.style.overflow = 'hidden';
  }

  function closeModal() {
    modal.classList.remove('is-open');
    document.body.style.overflow = '';
  }

  triggers.forEach((btn) => btn.addEventListener('click', (e) => {
    e.preventDefault();
    openModal();
  }));

  if (closeBtn) closeBtn.addEventListener('click', closeModal);
  if (backdrop) backdrop.addEventListener('click', closeModal);

  window.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && modal.classList.contains('is-open')) {
      closeModal();
    }
  });
}
