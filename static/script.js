/* === منصة الاختبار — JavaScript المتقدم === */

/* ═══════════════════════════════════════════════════ */
/* === نظام إشعارات Toast === */
/* ═══════════════════════════════════════════════════ */

function showToast(message, type) {
    var container = document.getElementById("toast-container");
    if (!container) return;

    var toast = document.createElement("div");
    toast.className = "toast toast-" + (type || "info");
    toast.setAttribute("role", "alert");

    var icon = "";
    if (type === "warning") {
        icon = '<svg class="toast-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>';
    } else if (type === "success") {
        icon = '<svg class="toast-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>';
    } else if (type === "danger") {
        icon = '<svg class="toast-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>';
    }

    toast.innerHTML = icon + '<span>' + message + '</span>';
    container.appendChild(toast);

    setTimeout(function () {
        toast.classList.add("toast-out");
        setTimeout(function () {
            if (toast.parentNode) toast.parentNode.removeChild(toast);
        }, 250);
    }, 4000);
}

/* ═══════════════════════════════════════════════════ */
/* === نظام المودال المخصص === */
/* ═══════════════════════════════════════════════════ */

function showConfirmModal(message, onConfirm) {
    var overlay = document.getElementById("confirm-modal");
    if (!overlay) return;

    var body = document.getElementById("modal-body");
    var confirmBtn = document.getElementById("modal-confirm");
    var cancelBtn = document.getElementById("modal-cancel");

    if (body) body.textContent = message;
    overlay.classList.add("modal-open");
    overlay.setAttribute("aria-hidden", "false");

    // تركيز زر المتابعة
    if (confirmBtn) confirmBtn.focus();

    function cleanup() {
        overlay.classList.remove("modal-open");
        overlay.setAttribute("aria-hidden", "true");
        confirmBtn.removeEventListener("click", confirmHandler);
        cancelBtn.removeEventListener("click", cancelHandler);
        overlay.removeEventListener("click", overlayHandler);
        document.removeEventListener("keydown", escHandler);
    }

    function confirmHandler() {
        cleanup();
        if (onConfirm) onConfirm();
    }

    function cancelHandler() {
        cleanup();
    }

    function overlayHandler(e) {
        if (e.target === overlay) cancelHandler();
    }

    function escHandler(e) {
        if (e.key === "Escape") cancelHandler();
    }

    confirmBtn.addEventListener("click", confirmHandler);
    cancelBtn.addEventListener("click", cancelHandler);
    overlay.addEventListener("click", overlayHandler);
    document.addEventListener("keydown", escHandler);
}

/* ═══════════════════════════════════════════════════ */
/* === تبديل الوضع الليلي === */
/* ═══════════════════════════════════════════════════ */

document.addEventListener("DOMContentLoaded", function () {
    var toggle = document.getElementById("theme-toggle");
    if (!toggle) return;

    toggle.addEventListener("click", function () {
        var current = document.documentElement.getAttribute("data-theme");
        var next = current === "dark" ? "light" : "dark";
        document.documentElement.setAttribute("data-theme", next);
        try {
            localStorage.setItem("theme", next);
        } catch (e) { /* تجاهل */ }
    });
});

/* ═══════════════════════════════════════════════════ */
/* === تعبئة الإجابات المحفوظة + تحديث التقدم === */
/* ═══════════════════════════════════════════════════ */

document.addEventListener("DOMContentLoaded", function () {
    var savedDataEl = document.getElementById("saved-answers-data");
    if (savedDataEl) {
        try {
            var saved = JSON.parse(savedDataEl.textContent || "{}");
            Object.keys(saved).forEach(function (key) {
                var val = saved[key];
                if (!val) return;
                var radio = document.querySelector(
                    'input[type="radio"][name="' + key + '"][value="' + val + '"]'
                );
                if (radio) {
                    radio.checked = true;
                    // تحديث fallback للـ :has
                    var label = radio.closest(".option");
                    if (label) label.classList.add("checked-fallback");
                }
            });
        } catch (e) {
            /* تجاهل أخطاء التحليل */
        }
    }
    updateProgress();
});

function updateProgress() {
    var form = document.getElementById("quiz-form");
    if (!form) return;

    var totalQuestions = form.querySelectorAll(".question-card").length;
    var answered = 0;

    form.querySelectorAll(".question-card").forEach(function (card) {
        var radios = card.querySelectorAll('input[type="radio"]');
        var isAnswered = false;
        radios.forEach(function (r) {
            if (r.checked) isAnswered = true;
            // تحديث fallback للـ :has
            var label = r.closest(".option");
            if (label) {
                if (r.checked) label.classList.add("checked-fallback");
                else label.classList.remove("checked-fallback");
            }
            // تحديث aria-checked
            if (label) {
                label.setAttribute("aria-checked", r.checked ? "true" : "false");
            }
        });
        // شارة السؤال المُجاب
        if (isAnswered) {
            card.classList.add("answered");
            answered++;
        } else {
            card.classList.remove("answered");
        }
    });

    var progressText = document.getElementById("progress-text");
    var progressFill = document.getElementById("progress-fill");

    if (progressText) {
        progressText.textContent = "تمت الإجابة على " + answered + " من " + totalQuestions;
    }
    if (progressFill) {
        var pct = totalQuestions > 0 ? (answered / totalQuestions) * 100 : 0;
        progressFill.style.width = pct + "%";
    }
}

/* ═══════════════════════════════════════════════════ */
/* === الظهور التدريجي لبطاقات الأسئلة (IntersectionObserver) === */
/* ═══════════════════════════════════════════════════ */

document.addEventListener("DOMContentLoaded", function () {
    var cards = document.querySelectorAll(".question-card");
    if (cards.length === 0) return;

    // احترام تفضيل تقليل الحركة — أظهر كل شيء فوراً
    if (window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
        cards.forEach(function (card) { card.classList.add("visible"); });
        return;
    }

    if ("IntersectionObserver" in window) {
        var observer = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (entry.isIntersecting) {
                    entry.target.classList.add("visible");
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.1, rootMargin: "0px 0px -40px 0px" });

        cards.forEach(function (card) { observer.observe(card); });
    } else {
        // fallback: أظهر الكل
        cards.forEach(function (card) { card.classList.add("visible"); });
    }
});

/* ═══════════════════════════════════════════════════ */
/* === التنقل بلوحة المفاتيح للخيارات === */
/* ═══════════════════════════════════════════════════ */

document.addEventListener("DOMContentLoaded", function () {
    var form = document.getElementById("quiz-form");
    if (!form) return;

    form.querySelectorAll(".option").forEach(function (label) {
        // Enter/Space لاختيار الخيار
        label.addEventListener("keydown", function (e) {
            if (e.key === "Enter" || e.key === " ") {
                e.preventDefault();
                var radio = label.querySelector('input[type="radio"]');
                if (radio) {
                    radio.checked = true;
                    updateProgress();
                }
            }
        });

        // أسهم الأعلى/الأسفل للتنقل بين خيارات نفس السؤال
        label.addEventListener("keydown", function (e) {
            if (e.key !== "ArrowUp" && e.key !== "ArrowDown") return;
            e.preventDefault();

            var questionId = label.getAttribute("data-question");
            var options = Array.prototype.slice.call(
                form.querySelectorAll('.option[data-question="' + questionId + '"]')
            );
            var currentIndex = options.indexOf(label);
            var nextIndex;

            if (e.key === "ArrowDown") {
                nextIndex = (currentIndex + 1) % options.length;
            } else {
                nextIndex = (currentIndex - 1 + options.length) % options.length;
            }

            var nextLabel = options[nextIndex];
            if (nextLabel) nextLabel.focus();
        });
    });
});

/* ═══════════════════════════════════════════════════ */
/* === التحقق قبل الإرسال (مودال بدل confirm) + حالة loading === */
/* ═══════════════════════════════════════════════════ */

document.addEventListener("DOMContentLoaded", function () {
    var form = document.getElementById("quiz-form");
    if (!form) return;

    var submitBtn = document.getElementById("submit-btn");
    var submitText = submitBtn ? submitBtn.querySelector(".btn-submit-text") : null;

    form.addEventListener("submit", function (e) {
        var totalQuestions = form.querySelectorAll(".question-card").length;
        var unanswered = 0;

        form.querySelectorAll(".question-card").forEach(function (card) {
            var radios = card.querySelectorAll('input[type="radio"]');
            var isAnswered = false;
            radios.forEach(function (r) {
                if (r.checked) isAnswered = true;
            });
            if (!isAnswered) unanswered++;
        });

        if (unanswered > 0 && !form.dataset.confirmed) {
            e.preventDefault();
            var msg = "لديك " + unanswered + " سؤال بدون إجابة. هل تريد المتابعة وإنهاء الاختبار؟";
            showConfirmModal(msg, function () {
                form.dataset.confirmed = "true";
                // محاكاة النقر على الإرسال بعد التأكيد
                triggerSubmit();
            });
        } else {
            // منع الحفظ التلقائي أثناء إرسال النموذج (يمنع سباق /save مع /submit)
            window._quizSubmitting = true;
            if (submitBtn) {
            // حالة loading
            submitBtn.classList.add("btn-loading");
            if (submitText) submitText.textContent = "جاري الإرسال...";
            // إضافة spinner
            if (!submitBtn.querySelector(".btn-spinner")) {
                var spinner = document.createElement("span");
                spinner.className = "btn-spinner";
                submitBtn.insertBefore(spinner, submitBtn.firstChild);
            }
            }
        }
    });

    function triggerSubmit() {
        window._quizSubmitting = true;
        if (submitBtn) {
            submitBtn.classList.add("btn-loading");
            if (submitText) submitText.textContent = "جاري الإرسال...";
            if (!submitBtn.querySelector(".btn-spinner")) {
                var spinner = document.createElement("span");
                spinner.className = "btn-spinner";
                submitBtn.insertBefore(spinner, submitBtn.firstChild);
            }
        }
        form.submit();
    }
});

/* ═══════════════════════════════════════════════════ */
/* === المؤقت الزمني التنازلي === */
/* ═══════════════════════════════════════════════════ */

document.addEventListener("DOMContentLoaded", function () {
    var timerEl = document.getElementById("quiz-timer");
    if (!timerEl) return; // المؤقت معطّل (QUIZ_TIMER_MINUTES = 0)

    var minutes = parseInt(timerEl.getAttribute("data-minutes"), 10) || 0;
    var remainingAttr = timerEl.getAttribute("data-remaining");
    var totalSeconds;
    if (remainingAttr && remainingAttr !== "" && !isNaN(parseInt(remainingAttr, 10))) {
        totalSeconds = parseInt(remainingAttr, 10);
    } else {
        totalSeconds = minutes * 60;
    }
    var remainingInput = document.getElementById("remaining_seconds");
    var form = document.getElementById("quiz-form");
    var submitted = false;

    function pad(n) {
        return n < 10 ? "0" + n : "" + n;
    }

    function syncRemainingInput() {
        if (remainingInput) remainingInput.value = totalSeconds;
    }
    syncRemainingInput();

    function updateTimer() {
        if (submitted) return;
        if (totalSeconds <= 0) {
            timerEl.textContent = "الوقت المتبقي: 00:00";
            timerEl.classList.add("timer-warning");
            syncRemainingInput();
            submitted = true;
            if (form) {
                form.submit();
            }
            return;
        }
        var m = Math.floor(totalSeconds / 60);
        var s = totalSeconds % 60;
        timerEl.textContent = "الوقت المتبقي: " + pad(m) + ":" + pad(s);

        if (totalSeconds <= 60) {
            timerEl.classList.add("timer-warning");
        } else {
            timerEl.classList.remove("timer-warning");
        }
        totalSeconds--;
        syncRemainingInput();
    }

    updateTimer();
    setInterval(updateTimer, 1000);
});

/* ═══════════════════════════════════════════════════ */
/* === منع الغش: تعطيل النسخ واللصق والقص وقائمة السياق === */
/* ═══════════════════════════════════════════════════ */

document.addEventListener("DOMContentLoaded", function () {
    var form = document.getElementById("quiz-form");
    if (!form) return; // هذه الحماية على صفحة /quiz فقط

    ["copy", "paste", "cut"].forEach(function (evt) {
        document.addEventListener(evt, function (e) {
            // السماح بعمليات النسخ المصرّح بها (مثل نسخ رمز الاستئناف)
            if (window._allowCopyOnce) {
                window._allowCopyOnce = false;
                return true;
            }
            e.preventDefault();
            return false;
        });
    });

    document.addEventListener("contextmenu", function (e) {
        e.preventDefault();
        return false;
    });
});

/* ═══════════════════════════════════════════════════ */
/* === كشف تبديل التبويب (toast بدل alert) === */
/* ═══════════════════════════════════════════════════ */

document.addEventListener("DOMContentLoaded", function () {
    var form = document.getElementById("quiz-form");
    if (!form) return; // على صفحة /quiz فقط

    var tabInput = document.getElementById("tab_switches");
    var count = 0;
    var wasHidden = false;

    function registerSwitch() {
        count++;
        if (tabInput) {
            tabInput.value = count;
        }
        showToast("تم اكتشاف مغادرة الصفحة. يُمنع تبديل التبويب أثناء الاختبار.", "warning");
    }

    document.addEventListener("visibilitychange", function () {
        if (document.hidden) {
            wasHidden = true;
        } else if (wasHidden) {
            wasHidden = false;
            registerSwitch();
        }
    });

    window.addEventListener("blur", function () {
        wasHidden = true;
    });
});

/* ═══════════════════════════════════════════════════ */
/* === الحفظ التلقائي للإجابات === */
/* ═══════════════════════════════════════════════════ */

document.addEventListener("DOMContentLoaded", function () {
    var form = document.getElementById("quiz-form");
    if (!form) return; // الحفظ على صفحة /quiz فقط

    var resumeCodeInput = document.getElementById("resume_code");
    var remainingInput = document.getElementById("remaining_seconds");
    var saveIndicator = document.getElementById("save-indicator");
    var resumeCode = resumeCodeInput ? resumeCodeInput.value : "";
    var saveUrl = "/save";
    var indicatorTimer = null;

    function collectAnswers() {
        var answers = {};
        form.querySelectorAll(".question-card").forEach(function (card) {
            var radios = card.querySelectorAll('input[type="radio"]');
            radios.forEach(function (r) {
                if (r.checked) {
                    answers[r.name] = r.value;
                }
            });
        });
        return answers;
    }

    function showSaved() {
        if (!saveIndicator) return;
        saveIndicator.style.display = "inline-block";
        saveIndicator.classList.add("save-success");
        if (indicatorTimer) clearTimeout(indicatorTimer);
        indicatorTimer = setTimeout(function () {
            saveIndicator.style.display = "none";
        }, 2000);
    }

    function buildPayload() {
        return {
            answers: collectAnswers(),
            remaining_seconds: remainingInput ? remainingInput.value : null,
            resume_code: resumeCode
        };
    }

    function saveAnswers() {
        var payload = buildPayload();
        return fetch(saveUrl, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
            keepalive: true
        }).then(function (resp) {
            if (resp.ok) showSaved();
        }).catch(function () { /* تجاهل أخطاء الحفظ الدوري */ });
    }

    // حفظ دوري كل 15 ثانية
    setInterval(saveAnswers, 15000);

    // حفظ عند مغادرة الصفحة عبر sendBeacon
    window.addEventListener("beforeunload", function () {
        if (window._quizSubmitting) return; // لا تحفظ أثناء الإرسال
        if (navigator.sendBeacon) {
            var blob = new Blob([JSON.stringify(buildPayload())], { type: "application/json" });
            navigator.sendBeacon(saveUrl, blob);
        }
    });

    // حفظ عند إخفاء الصفحة
    document.addEventListener("visibilitychange", function () {
        if (document.hidden && !window._quizSubmitting) {
            saveAnswers();
        }
    });
});

/* ═══════════════════════════════════════════════════ */
/* === زر نسخ رمز الاستئناف === */
/* ═══════════════════════════════════════════════════ */

document.addEventListener("DOMContentLoaded", function () {
    var copyBtn = document.getElementById("copy-resume-code");
    var codeEl = document.getElementById("resume-code-value");
    if (!copyBtn || !codeEl) return;

    copyBtn.addEventListener("click", function () {
        var code = codeEl.textContent.trim();
        var textEl = copyBtn.querySelector(".copy-btn-text");

        function onSuccess() {
            copyBtn.classList.add("copied");
            if (textEl) textEl.textContent = "تم النسخ ✓";
            showToast("تم نسخ رمز الاستئناف", "success");
            setTimeout(function () {
                copyBtn.classList.remove("copied");
                if (textEl) textEl.textContent = "نسخ";
            }, 2000);
        }

        if (navigator.clipboard && navigator.clipboard.writeText) {
            navigator.clipboard.writeText(code).then(onSuccess).catch(function () {
                fallbackCopy(code, onSuccess);
            });
        } else {
            fallbackCopy(code, onSuccess);
        }
    });

    function fallbackCopy(text, onSuccess) {
        var textarea = document.createElement("textarea");
        textarea.value = text;
        textarea.style.position = "fixed";
        textarea.style.opacity = "0";
        document.body.appendChild(textarea);
        textarea.select();
        // السماح بعملية النسخ هذه مرة واحدة (تجاوز منع الغش)
        window._allowCopyOnce = true;
        try {
            document.execCommand("copy");
            onSuccess();
        } catch (e) { /* تجاهل */ }
        window._allowCopyOnce = false;
        document.body.removeChild(textarea);
    }
});

/* ═══════════════════════════════════════════════════ */
/* === وضع ملء الشاشة === */
/* ═══════════════════════════════════════════════════ */

document.addEventListener("DOMContentLoaded", function () {
    var btn = document.getElementById("fullscreen-btn");
    if (!btn) return;

    btn.addEventListener("click", function () {
        if (!document.fullscreenElement) {
            if (document.documentElement.requestFullscreen) {
                document.documentElement.requestFullscreen();
            }
        } else {
            if (document.exitFullscreen) {
                document.exitFullscreen();
            }
        }
    });

    document.addEventListener("fullscreenchange", function () {
        btn.setAttribute("aria-label", document.fullscreenElement ? "الخروج من ملء الشاشة" : "ملء الشاشة");
    });
});
