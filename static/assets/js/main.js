(function () {
  "use strict";
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var norm = function (s) {
    return (s || "").toLowerCase().replace(/đ/g, "d").normalize("NFD").replace(/[̀-ͯ]/g, "").trim();
  };
  var CFG = window.GNN_CONFIG || {};

  /* ---------- Menu: mega/dropdown + mobile ---------- */
  $$(".nav-item > .nav-link").forEach(function (btn) {
    btn.addEventListener("click", function (e) {
      e.stopPropagation();
      var item = btn.parentElement, open = !item.classList.contains("open");
      $$(".nav-item.open").forEach(function (i) { if (i !== item) { i.classList.remove("open"); i.firstElementChild.setAttribute("aria-expanded", "false"); } });
      item.classList.toggle("open", open);
      btn.setAttribute("aria-expanded", open);
    });
  });
  if (window.matchMedia("(hover:hover) and (min-width:901px)").matches) {
    $$(".nav-item").forEach(function (item) {
      var t;
      item.addEventListener("mouseenter", function () { clearTimeout(t); $$(".nav-item.open").forEach(function (i) { i.classList.remove("open"); }); item.classList.add("open"); });
      item.addEventListener("mouseleave", function () { t = setTimeout(function () { item.classList.remove("open"); }, 180); });
    });
  }
  document.addEventListener("click", function (e) {
    if (!e.target.closest(".nav-item")) $$(".nav-item.open").forEach(function (i) { i.classList.remove("open"); });
    if (document.body.classList.contains("menu-open") && !e.target.closest(".nav") && !e.target.closest("#menuBtn")) toggleMenu(false);
  });
  var menuBtn = $("#menuBtn"), nav = $("#nav");
  function toggleMenu(on) {
    nav.classList.toggle("open", on);
    document.body.classList.toggle("menu-open", on);
    menuBtn.setAttribute("aria-expanded", on);
  }
  if (menuBtn) menuBtn.addEventListener("click", function (e) { e.stopPropagation(); toggleMenu(!nav.classList.contains("open")); });

  /* ---------- Tìm kiếm toàn site ---------- */
  var ov = $("#searchOv"), inp = $("#searchInput"), res = $("#searchRes"), idx = null, act = -1;
  function openSearch() {
    ov.hidden = false; document.body.style.overflow = "hidden"; inp.value = ""; render(""); setTimeout(function () { inp.focus(); }, 30);
    if (!idx) fetch("/search.json").then(function (r) { return r.json(); }).then(function (d) { idx = d; render(inp.value); }).catch(function () { res.innerHTML = "<p>Không tải được dữ liệu tìm kiếm.</p>"; });
  }
  function closeSearch() { ov.hidden = true; document.body.style.overflow = ""; }
  function esc(s) { return s.replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }
  function render(q) {
    act = -1;
    if (!idx) { res.innerHTML = "<p>Đang tải…</p>"; return; }
    var words = norm(q).split(/\s+/).filter(Boolean);
    var list = !words.length ? idx.slice(0, 6) : idx.map(function (it) {
      var sc = 0, t = norm(it.t);
      for (var i = 0; i < words.length; i++) { if (it.s.indexOf(words[i]) < 0) return null; sc += t.indexOf(words[i]) >= 0 ? 3 : 1; }
      return [sc, it];
    }).filter(Boolean).sort(function (a, b) { return b[0] - a[0]; }).map(function (x) { return x[1]; }).slice(0, 10);
    res.innerHTML = (!words.length ? "<p>Gợi ý bài viết:</p>" : "") + (list.length ? list.map(function (it) {
      return '<a href="' + it.u + '"><span class="sr-c">' + esc(it.c) + "</span><b>" + esc(it.t) + "</b><small>" + esc(it.d) + "</small></a>";
    }).join("") : "<p>Không tìm thấy kết quả cho “" + esc(q) + "”.</p>");
  }
  if (ov) {
    $("#openSearch").addEventListener("click", openSearch);
    $("#closeSearch").addEventListener("click", closeSearch);
    ov.addEventListener("click", function (e) { if (e.target === ov) closeSearch(); });
    inp.addEventListener("input", function () { render(inp.value); });
    inp.addEventListener("keydown", function (e) {
      var links = $$("a", res);
      if (e.key === "ArrowDown" || e.key === "ArrowUp") {
        e.preventDefault(); act = (act + (e.key === "ArrowDown" ? 1 : -1) + links.length) % links.length;
        links.forEach(function (l, i) { l.classList.toggle("act", i === act); });
      } else if (e.key === "Enter" && links.length) { e.preventDefault(); location.href = (links[act] || links[0]).href; }
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && !ov.hidden) closeSearch();
      if (e.key === "/" && ov.hidden && !/input|textarea/i.test(document.activeElement.tagName)) { e.preventDefault(); openSearch(); }
    });
  }

  /* ---------- Tabs trang chủ ---------- */
  $$('.tabs [role="tab"]').forEach(function (b) {
    b.addEventListener("click", function () {
      $$('.tabs [role="tab"]').forEach(function (x) { x.setAttribute("aria-selected", x === b); });
      $$(".tabpanel").forEach(function (p) { p.hidden = p.dataset.panel !== b.dataset.tab; });
    });
  });

  /* ---------- Lọc blog ---------- */
  var grid = $("#blogGrid");
  if (grid) {
    var cat = "all", q = $("#blogQ");
    var p = new URLSearchParams(location.search);
    if (p.get("q")) q.value = p.get("q");
    if (p.get("c")) cat = p.get("c");
    var apply = function () {
      var words = norm(q.value).split(/\s+/).filter(Boolean), n = 0;
      $$(".bi", grid).forEach(function (el) {
        var ok = (cat === "all" || el.dataset.cat === cat) && words.every(function (w) { return el.dataset.s.indexOf(w) >= 0; });
        el.hidden = !ok; if (ok) n++;
      });
      $("#blogEmpty").hidden = n > 0;
      $$(".filter .chip").forEach(function (c) { c.classList.toggle("on", c.dataset.f === cat); });
    };
    $$(".filter .chip").forEach(function (c) { c.addEventListener("click", function () { cat = c.dataset.f; apply(); }); });
    q.addEventListener("input", apply);
    apply();
  }

  /* ---------- Mục lục: đánh dấu mục đang đọc ---------- */
  var tocLinks = $$(".toc a");
  if (tocLinks.length && "IntersectionObserver" in window) {
    var map = {};
    tocLinks.forEach(function (a) { map[a.getAttribute("href").slice(1)] = a; });
    var io = new IntersectionObserver(function (ents) {
      ents.forEach(function (en) {
        if (en.isIntersecting) { tocLinks.forEach(function (a) { a.classList.remove("on"); }); var l = map[en.target.id]; if (l) l.classList.add("on"); }
      });
    }, { rootMargin: "-90px 0px -70% 0px" });
    Object.keys(map).forEach(function (id) { var h = document.getElementById(id); if (h) io.observe(h); });
  }

  /* ---------- Máy tính giờ ngủ ---------- */
  var calc = $("#calc");
  if (calc) {
    var mode = "wake", t = $("#calcTime"), out = $("#calcOut"), FALL = 15, CYC = 90;
    var pad = function (n) { return (n < 10 ? "0" : "") + n; };
    var fmt = function (m) { m = ((m % 1440) + 1440) % 1440; return pad(Math.floor(m / 60)) + ":" + pad(m % 60); };
    var run = function (fromNow) {
      var base;
      if (fromNow) { var d = new Date(); base = d.getHours() * 60 + d.getMinutes(); }
      else { if (!t.value) return; var s = t.value.split(":"); base = +s[0] * 60 + +s[1]; }
      var cycles = [6, 5, 4, 3], html = "";
      if (mode === "wake") {
        html = "<h3>Để thức dậy lúc <b>" + fmt(base) + "</b>, bạn nên lên giường vào một trong các giờ:</h3><div class='times'>" +
          cycles.map(function (c) { return "<div class='time" + (c >= 5 ? " best" : "") + "'><b>" + fmt(base - c * CYC - FALL) + "</b><small>" + c + " chu kỳ · " + (c * 1.5).toString().replace(".", ",") + " giờ ngủ" + (c >= 5 ? " · lý tưởng" : "") + "</small></div>"; }).join("") + "</div>";
      } else {
        html = "<h3>Nếu lên giường lúc <b>" + fmt(base) + "</b>, bạn nên đặt báo thức vào:</h3><div class='times'>" +
          cycles.slice().reverse().concat([]).sort(function (a, b) { return b - a; }).map(function (c) { return "<div class='time" + (c >= 5 ? " best" : "") + "'><b>" + fmt(base + FALL + c * CYC) + "</b><small>" + c + " chu kỳ · " + (c * 1.5).toString().replace(".", ",") + " giờ ngủ" + (c >= 5 ? " · lý tưởng" : "") + "</small></div>"; }).join("") + "</div>";
      }
      out.innerHTML = html + "<p class='small-note'>Đã tính thêm khoảng " + FALL + " phút để chìm vào giấc ngủ. Người trưởng thành nên ngủ 5–6 chu kỳ (7,5–9 giờ).</p>";
    };
    $$(".seg button", calc).forEach(function (b) {
      b.addEventListener("click", function () {
        mode = b.dataset.mode;
        $$(".seg button", calc).forEach(function (x) { x.classList.toggle("on", x === b); });
        $("#calcLabel").textContent = mode === "wake" ? "Giờ thức dậy" : "Giờ lên giường";
        t.value = mode === "wake" ? "06:00" : "22:30";
        $("#calcNow").hidden = mode === "wake";
        run();
      });
    });
    $("#calcNow").hidden = true;
    t.addEventListener("input", function () { run(); });
    $("#calcNow").addEventListener("click", function () {
      var d = new Date(); t.value = pad(d.getHours()) + ":" + pad(d.getMinutes()); run(true);
    });
    run();
  }

  /* ---------- Bài kiểm tra giấc ngủ ---------- */
  var quiz = $("#quiz");
  if (quiz) {
    var total = $$("fieldset", quiz).length;
    quiz.addEventListener("change", function () {
      var done = $$("input:checked", quiz).length;
      $("#quizBar").style.width = (done / total * 100) + "%";
    });
    quiz.addEventListener("submit", function (e) {
      e.preventDefault();
      var checked = $$("input:checked", quiz);
      if (checked.length < total) {
        var first = $$("fieldset", quiz).filter(function (f) { return !$("input:checked", f); })[0];
        first.scrollIntoView({ behavior: "smooth", block: "center" });
        first.querySelector("input").focus();
        return;
      }
      var score = checked.reduce(function (s, i) { return s + (+i.value); }, 0), max = total * 3;
      var r;
      if (score <= 5) r = ["#5b7552", "Giấc ngủ của bạn khá tốt", "Bạn đang có nền tảng giấc ngủ lành mạnh. Hãy duy trì giờ giấc đều đặn và những thói quen tốt.", '<a class="btn btn-navy" href="/ve-sinh-giac-ngu/">Giữ thói quen ngủ tốt</a>'];
      else if (score <= 11) r = ["#4f7392", "Giấc ngủ có dấu hiệu chưa ổn", "Bạn có một vài vấn đề về giấc ngủ. Điều chỉnh thói quen sinh hoạt thường giúp cải thiện rõ rệt trong vài tuần. Nếu không đỡ, hãy trao đổi với bác sĩ.", '<a class="btn btn-navy" href="/20-cach-ngu-ngon-va-sau/">20 cách ngủ ngon và sâu</a>'];
      else if (score <= 17) r = ["#d98a1f", "Có thể bạn đang bị mất ngủ", "Kết quả cho thấy giấc ngủ đang ảnh hưởng đáng kể đến bạn. Nên gặp bác sĩ để được đánh giá nguyên nhân – mất ngủ điều trị sớm sẽ dễ hơn nhiều.", '<a class="btn btn-gold" href="/lien-he/">Đặt lịch khám</a> <a class="btn btn-ghost" href="/dieu-tri-mat-ngu/">Các cách điều trị</a>'];
      else r = ["#c9443a", "Mất ngủ mức độ nặng", "Tình trạng ngủ kém đang ảnh hưởng nhiều đến sức khỏe và cuộc sống của bạn. Bạn nên đi khám bác sĩ chuyên khoa sớm để được điều trị phù hợp.", '<a class="btn btn-gold" href="/lien-he/">Đặt lịch khám ngay</a> <a class="btn btn-ghost" href="tel:' + (CFG.PHONE_RAW || "") + '">Gọi ' + (CFG.PHONE || "") + "</a>"];
      var extra = +checked[7].value >= 2 ? "<p><b>Lưu ý:</b> Dùng thuốc ngủ, rượu hay thuốc an thần thường xuyên để dễ ngủ cần được bác sĩ đánh giá – đừng tự tăng liều hoặc tự ngưng đột ngột. <a href='/thuoc-ngu-nhung-dieu-can-biet/'>Tìm hiểu thêm</a>.</p>" : "";
      var o = $("#quizOut");
      o.style.setProperty("--c", r[0]);
      o.innerHTML = "<p class='eyebrow' style='color:" + r[0] + "'>Kết quả của bạn</p><div class='score'>" + score + "<small style='font-size:20px;color:#5f6b59'>/" + max + "</small></div><h2>" + r[1] + "</h2><p>" + r[2] + "</p>" + extra + "<p>" + r[3] + "</p><p><button class='btn btn-ghost' type='button' id='quizAgain'>Làm lại</button></p>";
      o.hidden = false; quiz.hidden = true;
      o.scrollIntoView({ behavior: "smooth", block: "start" });
      $("#quizAgain").addEventListener("click", function () { quiz.reset(); $("#quizBar").style.width = 0; o.hidden = true; quiz.hidden = false; quiz.scrollIntoView({ behavior: "smooth" }); });
    });
  }

  /* ---------- Form đặt lịch ---------- */
  var form = $("#bookForm");
  if (form) {
    var today = new Date(), dt = form.querySelector('[name="ngay_hen"]');
    dt.min = today.toISOString().slice(0, 10);
    var msg = $("#formMsg");
    var show = function (cls, html) { msg.className = "form-msg " + cls; msg.innerHTML = html; msg.hidden = false; };
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      if (form._gotcha.value) return;
      var ok = true;
      ["ho_ten", "so_dien_thoai"].forEach(function (n) {
        var el = form[n], bad = !el.value.trim() || (n === "so_dien_thoai" && !/^[0-9 .+]{9,15}$/.test(el.value.trim()));
        el.classList.toggle("bad", bad); if (bad && ok) { el.focus(); ok = false; }
      });
      if (!ok) { show("err", "Vui lòng nhập họ tên và số điện thoại hợp lệ."); return; }
      var data = {};
      new FormData(form).forEach(function (v, k) { if (k !== "_gotcha") data[k] = v; });
      var text = "ĐẶT LỊCH KHÁM – giacngungon.org\nHọ tên: " + data.ho_ten + "\nSĐT: " + data.so_dien_thoai +
        (data.email ? "\nEmail: " + data.email : "") + (data.ngay_hen ? "\nNgày muốn khám: " + data.ngay_hen.split("-").reverse().join("/") : "") +
        (data.dia_chi ? "\nĐịa chỉ: " + data.dia_chi : "") + (data.loi_nhan ? "\nLời nhắn: " + data.loi_nhan : "");
      var fallback = function () {
        var base = "Cảm ơn bạn! Để được xác nhận lịch nhanh nhất, vui lòng <a href='" + CFG.ZALO + "' target='_blank' rel='noopener'>nhắn Zalo</a> hoặc <a href='tel:" + CFG.PHONE_RAW + "'>gọi " + CFG.PHONE + "</a>.";
        show("ok", base);
        try {
          if (navigator.clipboard && navigator.clipboard.writeText) {
            navigator.clipboard.writeText(text).then(function () {
              show("ok", base + " Nội dung đặt lịch đã được sao chép – bạn chỉ cần dán vào Zalo.");
            }, function () {});
          }
        } catch (_) {}
      };
      if (!CFG.WEB3FORMS_KEY) { fallback(); return; }
      var btn = form.querySelector("button[type=submit]"); btn.disabled = true; btn.textContent = "Đang gửi…";
      data.access_key = CFG.WEB3FORMS_KEY; data.subject = "Đặt lịch khám mới – " + data.ho_ten; data.from_name = "giacngungon.org"; data.message = text;
      fetch("https://api.web3forms.com/submit", { method: "POST", headers: { "Content-Type": "application/json", Accept: "application/json" }, body: JSON.stringify(data) })
        .then(function (r) { return r.json(); })
        .then(function (j) {
          if (j.success) { form.reset(); show("ok", "Đã gửi thành công! Phòng khám sẽ liên hệ với bạn sớm. Cần gấp, vui lòng gọi <a href='tel:" + CFG.PHONE_RAW + "'>" + CFG.PHONE + "</a>."); }
          else throw new Error();
        })
        .catch(fallback)
        .then(function () { btn.disabled = false; btn.textContent = "Gửi yêu cầu đặt lịch"; });
    });
  }
})();
