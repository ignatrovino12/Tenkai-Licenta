import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
	plugins: [sveltekit()],
	optimizeDeps: {
		exclude: ["@ffmpeg/ffmpeg", "@ffmpeg/util"],
	  },
	  server: {
		headers: {
		  "Cross-Origin-Opener-Policy": "same-origin",
		  "Cross-Origin-Embedder-Policy": "require-corp",
		},
		 proxy:{
			'/accounts': {
				target: 'http://web:8000/',
				changeOrigin: true,
			},
			'/api': 'http://web:8000/',
			'/admin': 'http://web:8000/',
			'/static': 'http://web:8000/',
		 }
	  },
});

