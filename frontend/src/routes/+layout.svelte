<script lang="ts">
	import '../app.css';
	import favicon from '$lib/assets/favicon.svg';
	import { onMount } from 'svelte';

	let { children } = $props();

	onMount(() => {
		// Initialize theme from localStorage or default to dark
		const savedTheme = localStorage.getItem('theme');
		if (savedTheme === 'light') {
			document.documentElement.classList.add('light-theme');
		} else {
			document.documentElement.classList.remove('light-theme');
		}
	});
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
	<title>Real Estate AI Assistant</title>
</svelte:head>

{@render children()}
