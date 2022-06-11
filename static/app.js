// Message for anyone that pulls up the dev tools on accident.
console.warn(
	'Hi there! It seems that you have found the developer tools. Notice how I said DEVELOPER in the previous sentence. If you are NOT a developer or you do not know what these tools are used for, kindly press F12 to leave this view. Thank you!'
);

// Once the DOM is ready, we are going to make a call to the API to get the pokemon sprites so that users can see little images in the master pokemon generations view.
$(document).ready(function() {
	makeImgCall();
});

// Enabling tool tip functionality from Bootstrap docs: https://getbootstrap.com/docs/5.1/components/tooltips/
let tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
let tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
	return new bootstrap.Tooltip(tooltipTriggerEl);
});

// selecting all class attributes from master pokemon generations view.
const allPokemon = document.querySelectorAll('.pokemon');

// Function makes API call for all pokemon that are listed in the master pokemon generation view and takes their ID to find the matching sprite. New image tag is then created and appended to the master generations view.
async function makeImgCall() {
	for (let i = 0; i < allPokemon.length; i++) {
		const res = await axios.get(`https://pokeapi.co/api/v2/pokemon/${allPokemon[i].id}/`);
		const data = res.data;
		const imgSrc = data.sprites.front_default;

		let parent = allPokemon[i].parentElement;
		const newImgTag = document.createElement('img');
		newImgTag.setAttribute('src', imgSrc);
		newImgTag.setAttribute('alt', 'pokemon-default-image');
		newImgTag.setAttribute('height', 48);
		newImgTag.setAttribute('width', 48);

		parent.append(newImgTag);
	}
}
