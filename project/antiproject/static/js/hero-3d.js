let scene, camera, renderer, starGeo, stars, mesh;

function init() {
    scene = new THREE.Scene();

    camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 1, 1000);
    camera.position.z = 100;
    camera.rotation.x = Math.PI / 2;

    renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    document.getElementById('three-container').appendChild(renderer.domElement);

    // Starfield
    starGeo = new THREE.BufferGeometry();
    const starCoords = [];
    for (let i = 0; i < 6000; i++) {
        starCoords.push(
            Math.random() * 600 - 300,
            Math.random() * 600 - 300,
            Math.random() * 600 - 300
        );
    }
    starGeo.setAttribute('position', new THREE.Float32BufferAttribute(starCoords, 3));

    let sprite = new THREE.TextureLoader().load('https://threejs.org/examples/textures/sprites/disc.png');
    let starMaterial = new THREE.PointsMaterial({
        color: 0x00f2ff,
        size: 0.7,
        map: sprite,
        transparent: true
    });

    stars = new THREE.Points(starGeo, starMaterial);
    scene.add(stars);

    // Futuristic Object
    const geometry = new THREE.IcosahedronGeometry(30, 2);
    const material = new THREE.MeshPhongMaterial({
        color: 0x00f2ff,
        wireframe: true,
        transparent: true,
        opacity: 0.5,
        emissive: 0x00f2ff,
        emissiveIntensity: 0.5
    });
    mesh = new THREE.Mesh(geometry, material);
    mesh.position.set(0, 0, 0);
    scene.add(mesh);

    // Lights
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
    scene.add(ambientLight);

    const pointLight = new THREE.PointLight(0xbc00ff, 2);
    pointLight.position.set(50, 50, 50);
    scene.add(pointLight);

    window.addEventListener('resize', onWindowResize, false);
    document.addEventListener('mousemove', onMouseMove, false);

    animate();
}

function onWindowResize() {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
}

let mouseX = 0, mouseY = 0;
function onMouseMove(event) {
    mouseX = (event.clientX - window.innerWidth / 2) / 100;
    mouseY = (event.clientY - window.innerHeight / 2) / 100;
}

function animate() {
    requestAnimationFrame(animate);

    // Star animation
    const positions = starGeo.attributes.position.array;
    for (let i = 1; i < positions.length; i += 3) {
        positions[i] -= 0.5;
        if (positions[i] < -300) {
            positions[i] = 300;
        }
    }
    starGeo.attributes.position.needsUpdate = true;
    stars.rotation.y += 0.002;

    // Mesh animation
    mesh.rotation.x += 0.005;
    mesh.rotation.y += 0.005;
    
    // Parallax effect based on mouse
    gsap.to(mesh.rotation, {
        y: mesh.rotation.y + mouseX * 0.5,
        x: mesh.rotation.x + mouseY * 0.5,
        duration: 2
    });
    
    gsap.to(camera.position, {
        x: mouseX * 2,
        y: -mouseY * 2,
        duration: 2
    });

    renderer.render(scene, camera);
}

init();
