

// function fetchSourceFacts(
//   url: string
// ): Observable<SourceFacts> {

//   /* Try to match GitHub repository */
//   let match = url.match(/^.+github\.com\/([^/]+)\/?([^/]+)?/i)
//   if (match) {
//     const [, user, repo] = match
//     return fetchSourceFactsFromGitHub(user, repo)
//   }

//   /* Try to match GitLab repository */
//   match = url.match(/^.+?([^/]*gitlab[^/]+)\/(.+?)\/?$/i)
//   if (match) {
//     const [, base, slug] = match
//     return fetchSourceFactsFromGitLab(base, slug)
//   }

//   /* Fallback */
//   return EMPTY
// }

// function fetchSourceFactsFromGitLab(
//   base: string, project: string
// ): Observable<SourceFacts> {
//   const url = `https://${base}/api/v4/projects/${encodeURIComponent(project)}`
//   return requestJSON<ProjectSchema>(url)
//     .pipe(
//       catchError(() => EMPTY), // @todo refactor instant loading
//       map(({ star_count, forks_count }) => ({
//         stars: star_count,
//         forks: forks_count
//       })),
//       defaultIfEmpty({})
//     )
// }

// function fetchSourceFactsFromGitHub(
//   user: string, repo?: string
// ): Observable<SourceFacts> {
//   if (typeof repo !== "undefined") {
//     const url = `https://api.github.com/repos/${user}/${repo}`
//     return zip(

//       /* Fetch version */
//       requestJSON<Release>(`${url}/releases/latest`)
//         .pipe(
//           catchError(() => EMPTY), // @todo refactor instant loading
//           map(release => ({
//             version: release.tag_name
//           })),
//           defaultIfEmpty({})
//         ),

//       /* Fetch stars and forks */
//       requestJSON<Repo>(url)
//         .pipe(
//           catchError(() => EMPTY), // @todo refactor instant loading
//           map(info => ({
//             stars: info.stargazers_count,
//             forks: info.forks_count
//           })),
//           defaultIfEmpty({})
//         )
//     )
//       .pipe(
//         map(([release, info]) => ({ ...release, ...info }))
//       )

//   /* User or organization */
//   } else {
//     const url = `https://api.github.com/users/${user}`
//     return requestJSON<User>(url)
//       .pipe(
//         map(info => ({
//           repositories: info.public_repos
//         })),
//         defaultIfEmpty({})
//       )
//   }
// }
