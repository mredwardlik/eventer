// The address of the backend. Set API_URL when building for a server:
//   API_URL=https://events.example.com/api/v1/ npm run build
export const API_URL: string = process.env.API_URL || "http://localhost:8000/api/v1/";
