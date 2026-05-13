document.addEventListener("DOMContentLoaded", () => {
    const canvas = document.getElementById("canvas-limpieza");
    if (!canvas) return;

    const ctx = canvas.getContext("2d", { willReadFrequently: true });
    const pibbleSucio = document.getElementById("pibble-sucio");
    const boton = document.getElementById("boton-login");
    const barra = document.getElementById("barra-progreso");
    const mensaje = document.getElementById("mensaje");
    const porcentajeTexto = document.getElementById("porcentaje");

    let dibujando = false;
    let pixelesIniciales = null;
    let pixelesTotalesOpacos = 0;
    let lastX = null;
    let lastY = null;

    function ajustarCanvas() {
        const rect = pibbleSucio.getBoundingClientRect();
        if (rect.width === 0 || rect.height === 0) return;

        const dpr = window.devicePixelRatio || 1;

        // Tamaño REAL del canvas (alta resolución)
        canvas.width = rect.width * dpr;
        canvas.height = rect.height * dpr;

        // Tamaño VISUAL (CSS)
        canvas.style.width = rect.width + "px";
        canvas.style.height = rect.height + "px";

        // Resetear escala antes de aplicar (evita bugs en resize)
        ctx.setTransform(1, 0, 0, 1, 0, 0);
        ctx.scale(dpr, dpr);
        ctx.imageSmoothingEnabled = false;

        ctx.clearRect(0, 0, canvas.width, canvas.height);

        const img = pibbleSucio;

        const naturalRatio = img.naturalWidth / img.naturalHeight;
        const containerRatio = rect.width / rect.height;

        let drawWidth, drawHeight, offsetX, offsetY;

        // Simula object-fit: contain
        if (naturalRatio > containerRatio) {
            drawWidth = rect.width;
            drawHeight = rect.width / naturalRatio;
            offsetX = 0;
            offsetY = (rect.height - drawHeight) / 2;
        } else {
            drawHeight = rect.height;
            drawWidth = rect.height * naturalRatio;
            offsetX = (rect.width - drawWidth) / 2;
            offsetY = 0;
        }

        ctx.drawImage(
            pibbleSucio,
            0,
            0,
            img.naturalWidth,
            img.naturalHeight,
            offsetX,
            offsetY,
            drawWidth,
            drawHeight
        );

        // Guardar estado inicial
        pixelesIniciales = ctx.getImageData(0, 0, canvas.width, canvas.height);

        const data = pixelesIniciales.data;
        pixelesTotalesOpacos = 0;

        for (let i = 3; i < data.length; i += 4) {
            if (data[i] > 0) {
                pixelesTotalesOpacos++;
            }
        }

        pibbleSucio.style.visibility = "hidden";

        actualizarProgreso();
    }

    function inicializarCanvas() {
        if (pibbleSucio.complete && pibbleSucio.naturalWidth > 0) {
            ajustarCanvas();
        } else {
            pibbleSucio.onload = ajustarCanvas;
        }
    }

    window.addEventListener("resize", ajustarCanvas);
    inicializarCanvas();

    function limpiar(x, y) {
        const brushSize = canvas.offsetWidth * 0.07; // ajusta tamaño aquí

        ctx.save();
        ctx.globalCompositeOperation = "destination-out";
        ctx.beginPath();
        ctx.arc(x, y, brushSize, 0, Math.PI * 2);
        ctx.fill();
        ctx.restore();
    }

    function actualizarProgreso() {
        if (!pixelesIniciales || pixelesTotalesOpacos === 0) {
            barra.style.width = "0%";
            if (porcentajeTexto) porcentajeTexto.textContent = "0%";
            return;
        }

        const imageDataActual = ctx.getImageData(
            0,
            0,
            canvas.width,
            canvas.height
        );

        const actual = imageDataActual.data;
        const inicial = pixelesIniciales.data;

        let borrados = 0;

        for (let i = 3; i < actual.length; i += 4) {
            // Solo contar píxeles que originalmente eran visibles
            if (inicial[i] > 0 && actual[i] === 0) {
                borrados++;
            }
        }

        let porcentaje = Math.round(
            (borrados / pixelesTotalesOpacos) * 100
        );

        porcentaje = Math.min(Math.max(porcentaje, 0), 100);

        barra.style.width = porcentaje + "%";
        if (porcentajeTexto) {
            porcentajeTexto.textContent = porcentaje + "%";
        }

        if (porcentaje >= 100) {
            barra.style.width = "100%";
            if (porcentajeTexto) porcentajeTexto.textContent = "100%";
            boton.classList.add("activo");
            mensaje.innerHTML = "¡YAAAAAAAAAAY!";

            boton.scrollIntoView({ behavior: 'smooth', block: 'center' })
        }
    }

    function obtenerPosicion(e) {
        const rect = canvas.getBoundingClientRect();
        if (e.touches) {
            return {
                x: e.touches[0].clientX - rect.left,
                y: e.touches[0].clientY - rect.top,
            };
        }
        return {
            x: e.clientX - rect.left,
            y: e.clientY - rect.top,
        };
    }

    function iniciarDibujo(e) {
        dibujando = true;
        canvas.classList.add("canvas-activo");

        const pos = obtenerPosicion(e);

        ultimaX = pos.x;
        ultimaY = pos.y;

        limpiar(pos.x, pos.y);
        actualizarProgreso();
    }

    function dibujar(e) {
        if (!dibujando) return;
        e.preventDefault();

        const pos = obtenerPosicion(e);

        if (lastX !== null && lastY !== null) {
            const dx = pos.x - lastX;
            const dy = pos.y - lastY;
            const distancia = Math.sqrt(dx * dx + dy * dy);

            for (let i = 0; i < distancia; i += 5) {
                const x = lastX + (dx * i) / distancia;
                const y = lastY + (dy * i) / distancia;
                limpiar(x, y);
            }
        }

        limpiar(pos.x, pos.y);

        lastX = pos.x;
        lastY = pos.y;

    actualizarProgreso()
    }

    function detenerDibujo() {
        dibujando = false;
        lastX = null;
        lastY = null;
        canvas.classList.remove("canvas-activo");
    }

    canvas.addEventListener("mousedown", iniciarDibujo);
    canvas.addEventListener("mousemove", dibujar);
    canvas.addEventListener("mouseup", detenerDibujo);
    canvas.addEventListener("mouseleave", detenerDibujo);

    canvas.addEventListener("touchstart", (e) => {
        e.preventDefault();
        iniciarDibujo(e);
    }, { passive: false });

    canvas.addEventListener("touchmove", (e) => {
        e.preventDefault();
        dibujar(e);
    }, { passive: false });

    canvas.addEventListener("touchend", (e) => {
        e.preventDefault();
        detenerDibujo();
    });
    function enviarAltura() {
        const body = document.body;
        const html = document.documentElement;
        const altura = Math.max(body.scrollHeight, body.offsetHeight, html.clientHeight, html.scrollHeight, html.offsetHeight);
    
        window.parent.postMessage({
            type: "resize-iframe",
            height: altura + 50 // Un extra para que no se corte el porcentaje
        }, "*");
    }

    window.addEventListener("load", () => {
        enviarAltura();
        setTimeout(enviarAltura, 200);
        setTimeout(enviarAltura, 500);
    });


    const observer = new MutationObserver(() => {
        enviarAltura();
    });
    observer.observe(document.getElementById("contenedor-pibble"), {
        childList: true,
        subtree: true,
    });

    document.addEventListener('keydown', function (event) {
        if ((event.ctrlKey === true || event.metaKey === true) && 
        (event.which === 61 || event.which === 107 || event.which === 173 || event.which === 109 || event.which === 187 || event.which === 189)) {
            event.preventDefault();
        }
    }, false);

    document.addEventListener('keydown', function(e) {
        if (e.ctrlKey || e.metaKey) {
            switch (e.key) {
                case '+':
                case '=':
                case '-':
                case '_':
                case '0':
                    e.preventDefault();
                    break;
            }
        }
    }, false);

    // También bloquea el zoom con la rueda del ratón + Ctrl
    document.addEventListener('wheel', function(e) {
        if (e.ctrlKey) {
            e.preventDefault();
        }
    }, { passive: false });
});