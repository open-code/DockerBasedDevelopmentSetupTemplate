FROM node:14.4.0
# set working directory
WORKDIR /app
# copy and install app dependencies
# COPY package.json /app/package.json
# Temp commands to update all the dependencies - rajith, commment once dependencies are updated

# RUN npm i -g npm-check-updates
# RUN ncu -u

# end of dependency update commands
# RUN npm install
RUN npm install -g @angular/cli@latest
# add app
# start app
CMD ["./start.sh"]
