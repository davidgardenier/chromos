      program integflux
c
      implicit none
      character*50 dum,infile
      double precision e(10000),edel(10000),bflux(10000),berr(10000)
      double precision mod(10000),totflux,toterr,e1,e2,e3,e4,e5,e6
      double precision softflux,softerr,hardflux,harderr,hr,hrerr
      integer i,npoints
      
      open (unit=2,file='integflux.in',status='old')
      read (2,*) infile,e1,e2,e3,e4,e5,e6
      close (unit=2)

      open (unit=2,file=infile,status='old')
      read (2,*) dum
      read (2,*) dum
      read (2,*) dum
      do i=1,10000
        read (2,*,end=10) e(i),edel(i),bflux(i),berr(i),mod(i)
      enddo
 10   npoints=i-1

      call intcalc(e,edel,bflux,berr,npoints,e1,e2,totflux,toterr)
      call intcalc(e,edel,bflux,berr,npoints,e3,e4,softflux,softerr)
      call intcalc(e,edel,bflux,berr,npoints,e5,e6,hardflux,harderr)

      hr=hardflux/softflux
      hrerr=sqrt((harderr/softflux)**2+
     *((hardflux*softerr)/(softflux**2))**2)

      print *, "Flux from ",e1," to ",e2," is : ",totflux," +/- ",
     *toterr
      print *, "Hardness ratio is : ",hr," +/- ",hrerr

      open (unit=3,file='hardint.out',status='new')
      if (hr.lt.0.or.(hr/hrerr).lt.3.0) then
      hr = 0.0
      hrerr = 0.0
      endif

      write (3,220) totflux,toterr,hr,hrerr

 220  format(1P,e11.4e2,1x,e11.4e2,0P,2(1x,f10.5))


      end

      subroutine intcalc(e,edel,bflux,berr,npoints,en1,en2,intflux,
     *interr)
c
      implicit none
      double precision e(10000),edel(10000),bflux(10000),berr(10000)
      double precision intflux,interr,en1,en2
      integer i,npoints

      intflux=0.0
      interr=0.0

      do i=1,npoints
        if (en1.ge.(e(i)-edel(i)).and.en1.lt.(e(i)+edel(i))) then
        intflux=intflux+(((e(i)+edel(i))-en1)*bflux(i))
        interr=interr+(((e(i)+edel(i))-en1)*berr(i))**2
        else if (en1.lt.(e(i)-edel(i)).and.en2.ge.(e(i)+edel(i))) then
        intflux=intflux+(2*edel(i)*bflux(i))
        interr=interr+(edel(i)*berr(i))**2
        else if (en2.ge.(e(i)-edel(i)).and.en2.lt.(e(i)+edel(i))) then
        intflux=intflux+((en2-(e(i)-edel(i)))*bflux(i))
        interr=interr+((en2-(e(i)-edel(i)))*berr(i))**2
        endif
      enddo

      interr=sqrt(interr)
      intflux=intflux*1.60219e-9
      interr=interr*1.60219e-9

      return

      end
