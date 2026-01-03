// 获取轮播相关元素
const carouselImgs = document.querySelectorAll('.carousel-img');
const prevBtn = document.querySelector('.prev-btn');
const nextBtn = document.querySelector('.next-btn');
let currentIndex = 0; // 当前显示的图片索引

// 切换图片函数
function switchImg(index) {
    // 先隐藏所有图片
    carouselImgs.forEach(img => {
        img.classList.remove('active');
    });
    // 显示对应索引的图片
    carouselImgs[index].classList.add('active');
}

// 上一张按钮点击事件
prevBtn.addEventListener('click', () => {
    currentIndex--;
    // 如果索引小于0，切换到最后一张
    if (currentIndex < 0) {
        currentIndex = carouselImgs.length - 1;
    }
    switchImg(currentIndex);
});

// 下一张按钮点击事件
nextBtn.addEventListener('click', () => {
    currentIndex++;
    // 如果索引大于等于图片总数，切换到第一张
    if (currentIndex >= carouselImgs.length) {
        currentIndex = 0;
    }
    switchImg(currentIndex);
});

// 自动轮播（每3秒切换一次）
setInterval(() => {
    currentIndex++;
    if (currentIndex >= carouselImgs.length) {
        currentIndex = 0;
    }
    switchImg(currentIndex);
}, 3000);