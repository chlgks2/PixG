# PixG — 실행 환경

## 두 환경에서 돌렸습니다

| 환경 | GPU | VRAM | RAM | OS |
|---|---|---|---|---|
| 개인 노트북 | **RTX 3060 Laptop** | **6,144 MB** | 16,049 MB | Windows |
| 아카데미 서버 | RTX 4090 | 24,217 MB | 64,107 MB | Linux |

ComfyUI 기동 로그 원문입니다.

```
# 개인 노트북
Total VRAM 6144 MB, total RAM 16049 MB
Device: cuda:0 NVIDIA GeForce RTX 3060 Laptop GPU : cudaMallocAsync

# 아카데미 서버
Total VRAM 24217 MB, total RAM 64107 MB
Device: cuda:0 NVIDIA GeForce RTX 4090 : cudaMallocAsync
Set vram state to: NORMAL_VRAM
```

## VRAM 6GB가 문제였습니다

AnimateDiff는 단일 이미지가 아니라 **16프레임을 한 번에** 생성합니다. 단일 이미지 생성보다 VRAM을 훨씬 많이 쓰는데, 개인 작업 환경은 **VRAM 4배 차이가 나는 6GB**였습니다.

대응은 두 가지였습니다.

1. **가상메모리 확장**
2. **배치사이즈 조절** — `EmptyLatentImage` 의 `batch_size` 를 `16 → 1` 로 내린 흔적이 워크플로우에 남아 있습니다

무거운 실험은 아카데미의 4090 서버에서 돌렸습니다.

> 로그에 OOM 스택트레이스는 남아 있지 않아, "VRAM 몇 GB 지점에서 무엇이 터졌는지"는 기록으로 확인되지 않습니다. 환경 사양과 대응 방법까지만 적어둡니다.

## 소프트웨어

| 항목 | 버전 |
|---|---|
| PyTorch | 2.1.0 + cu121 |
| Python | 3.11 (ComfyUI portable embedded) |
| ComfyUI | 2023년 11월 시점 |

## 필요한 커스텀 노드

```
ComfyUI-AnimateDiff-Evolved
ComfyUI-Advanced-ControlNet
comfyui_controlnet_aux
ComfyUI-VideoHelperSuite
ComfyUI_FizzNodes
ComfyUI_Comfyroll_CustomNodes
efficiency-nodes-comfyui
ComfyUI-Custom-Scripts
```

ComfyUI-Manager 로 설치하면 됩니다.

## 후처리 스크립트 의존성

```bash
pip install transparent-background opencv-python pillow imageio numpy matplotlib
```

`transparent-background` 가 InSPyReNet 가중치를 최초 실행 시 자동으로 내려받습니다.
